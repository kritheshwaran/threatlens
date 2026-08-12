from unittest.mock import MagicMock, patch

import dns.exception
import dns.resolver

from backend.app.services.dns_analyzer import analyze_dns


def test_analyze_dns_empty_hostname():
    result = analyze_dns('')
    assert result['resolved'] is False
    for record_type, data in result['records'].items():
        assert data['records'] == []
        assert data['error']


def test_analyze_dns_structure_for_real_lookup():
    # Exercises the real resolver end-to-end; only structure is asserted
    # since actual record content depends on live network conditions.
    result = analyze_dns('example.com')
    assert result['hostname'] == 'example.com'
    assert set(result['records'].keys()) == {'A', 'AAAA', 'MX', 'NS', 'TXT'}
    assert isinstance(result['resolved'], bool)


@patch('backend.app.services.dns_analyzer.dns.resolver.Resolver')
def test_analyze_dns_handles_nxdomain(mock_resolver_cls):
    mock_resolver = MagicMock()
    mock_resolver.resolve.side_effect = dns.resolver.NXDOMAIN()
    mock_resolver_cls.return_value = mock_resolver

    result = analyze_dns('this-domain-does-not-exist-abcxyz.invalid')

    assert result['resolved'] is False
    assert result['records']['A']['error'] == 'domain does not exist'
    assert result['records']['MX']['error'] == 'domain does not exist'


@patch('backend.app.services.dns_analyzer.dns.resolver.Resolver')
def test_analyze_dns_handles_timeout(mock_resolver_cls):
    mock_resolver = MagicMock()
    mock_resolver.resolve.side_effect = dns.exception.Timeout()
    mock_resolver_cls.return_value = mock_resolver

    result = analyze_dns('example.com')

    assert result['resolved'] is False
    assert result['records']['A']['error'] == 'lookup timed out'


@patch('backend.app.services.dns_analyzer.dns.resolver.Resolver')
def test_analyze_dns_no_answer_is_not_an_error(mock_resolver_cls):
    mock_resolver = MagicMock()
    mock_resolver.resolve.side_effect = dns.resolver.NoAnswer()
    mock_resolver_cls.return_value = mock_resolver

    result = analyze_dns('example.com')

    assert result['records']['TXT']['records'] == []
    assert result['records']['TXT']['error'] is None


@patch('backend.app.services.dns_analyzer.dns.resolver.Resolver')
def test_analyze_dns_successful_mixed_records(mock_resolver_cls):
    mock_a_answer = MagicMock()
    mock_a_answer.to_text.return_value = '93.184.216.34'

    mock_resolver = MagicMock()

    def resolve_side_effect(hostname, record_type):
        if record_type == 'A':
            return [mock_a_answer]
        raise dns.resolver.NoAnswer()

    mock_resolver.resolve.side_effect = resolve_side_effect
    mock_resolver_cls.return_value = mock_resolver

    result = analyze_dns('example.com')

    assert result['resolved'] is True
    assert result['records']['A']['records'] == ['93.184.216.34']
    assert result['records']['MX']['records'] == []
    assert result['records']['MX']['error'] is None