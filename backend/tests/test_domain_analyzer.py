from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from backend.app.services.domain_analyzer import (
    analyze_domain,
    get_registrable_domain,
    get_subdomain,
)


def test_get_registrable_domain_simple():
    assert get_registrable_domain('mail.example.com') == 'example.com'


def test_get_registrable_domain_bare_domain():
    assert get_registrable_domain('example.com') == 'example.com'


def test_get_registrable_domain_multi_part_tld():
    assert get_registrable_domain('www.example.co.uk') == 'example.co.uk'


def test_get_registrable_domain_deep_subdomain():
    assert get_registrable_domain('a.b.c.example.com') == 'example.com'


def test_get_subdomain_present():
    assert get_subdomain('mail.example.com', 'example.com') == 'mail'


def test_get_subdomain_absent():
    assert get_subdomain('example.com', 'example.com') == ''


def test_analyze_domain_for_ip_address():
    result = analyze_domain('http://192.168.1.1/login')
    assert result['is_ip'] is True
    assert result['registrable_domain'] == '192.168.1.1'
    assert result['whois']['available'] is False
    assert result['whois']['error']


def test_analyze_domain_handles_unreachable_or_missing_whois_gracefully():
    # Never raises, regardless of whether the WHOIS server is reachable
    # from the current network -- only structure is guaranteed.
    result = analyze_domain('http://this-domain-should-not-exist-abcxyz123.invalid')
    assert 'whois' in result
    assert isinstance(result['whois']['available'], bool)
    if not result['whois']['available']:
        assert result['whois']['error']


@patch('backend.app.services.domain_analyzer._whois_lib')
def test_analyze_domain_successful_whois_lookup_is_parsed(mock_whois_lib):
    fake_record = MagicMock()
    fake_record.domain_name = 'EXAMPLE.COM'
    fake_record.registrar = 'Example Registrar, Inc.'
    fake_record.creation_date = datetime(2000, 1, 1, tzinfo=timezone.utc)
    fake_record.expiration_date = datetime(2030, 1, 1, tzinfo=timezone.utc)
    fake_record.updated_date = datetime(2023, 1, 1, tzinfo=timezone.utc)
    fake_record.status = ['clientTransferProhibited']
    fake_record.name_servers = ['ns1.example.com', 'ns2.example.com']
    mock_whois_lib.whois.return_value = fake_record

    result = analyze_domain('https://example.com')

    assert result['whois']['available'] is True
    assert result['whois']['registrar'] == 'Example Registrar, Inc.'
    assert result['whois']['domain_age_days'] > 0
    assert result['whois']['days_until_expiry'] > 0
    assert 'ns1.example.com' in result['whois']['name_servers']
    assert 'clientTransferProhibited' in result['whois']['status']


@patch('backend.app.services.domain_analyzer._whois_lib')
def test_analyze_domain_handles_whois_exception(mock_whois_lib):
    mock_whois_lib.whois.side_effect = TimeoutError('whois server unreachable')

    result = analyze_domain('https://example.com')

    assert result['whois']['available'] is False
    assert 'TimeoutError' in result['whois']['error']


@patch('backend.app.services.domain_analyzer._whois_lib')
def test_analyze_domain_handles_no_matching_record(mock_whois_lib):
    fake_record = MagicMock()
    fake_record.domain_name = None
    mock_whois_lib.whois.return_value = fake_record

    result = analyze_domain('https://example.com')

    assert result['whois']['available'] is False