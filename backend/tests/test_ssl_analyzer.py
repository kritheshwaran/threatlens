from unittest.mock import MagicMock, patch

from backend.app.services.ssl_analyzer import analyze_ssl


def test_analyze_ssl_no_hostname():
    result = analyze_ssl('')
    assert result['has_ssl'] is False
    assert result['error']


def test_analyze_ssl_dns_resolution_failure_is_handled():
    result = analyze_ssl('this-domain-should-not-exist-abcxyz123.invalid', timeout=3)
    assert result['has_ssl'] is False
    assert result['error']


def test_analyze_ssl_connection_refused_is_handled():
    # Nothing listens on port 81 on localhost by default in virtually
    # any environment, so this reliably exercises the refused-connection path.
    result = analyze_ssl('127.0.0.1', port=81, timeout=3)
    assert result['has_ssl'] is False
    assert result['error']


def test_analyze_ssl_https_real_lookup_structure():
    # Exercises a real TLS handshake end-to-end; only structure is
    # asserted since exact cert fields depend on the live network.
    result = analyze_ssl('example.com')
    assert 'has_ssl' in result
    if result['has_ssl']:
        assert 'certificate_valid' in result
        assert 'protocol_version' in result


def _mock_tls_connection(mock_context_factory, mock_create_connection, cert: dict):
    mock_ssl_socket = MagicMock()
    mock_ssl_socket.getpeercert.return_value = cert
    mock_ssl_socket.cipher.return_value = ('TLS_AES_256_GCM_SHA384', 'TLSv1.3', 256)
    mock_ssl_socket.version.return_value = 'TLSv1.3'
    mock_ssl_socket.__enter__.return_value = mock_ssl_socket
    mock_ssl_socket.__exit__.return_value = False

    mock_context = MagicMock()
    mock_context.wrap_socket.return_value = mock_ssl_socket
    mock_context_factory.return_value = mock_context

    mock_raw_socket = MagicMock()
    mock_raw_socket.__enter__.return_value = mock_raw_socket
    mock_raw_socket.__exit__.return_value = False
    mock_create_connection.return_value = mock_raw_socket


@patch('backend.app.services.ssl_analyzer.socket.create_connection')
@patch('backend.app.services.ssl_analyzer.ssl.create_default_context')
def test_analyze_ssl_successful_certificate_is_parsed(mock_context_factory, mock_create_connection):
    fake_cert = {
        'issuer': ((('organizationName', 'Example CA'),), (('commonName', 'Example CA Root'),)),
        'subject': ((('commonName', 'example.com'),),),
        'notBefore': 'Jan  1 00:00:00 2024 GMT',
        'notAfter': 'Jan  1 00:00:00 2030 GMT',
        'subjectAltName': (('DNS', 'example.com'), ('DNS', 'www.example.com')),
    }
    _mock_tls_connection(mock_context_factory, mock_create_connection, fake_cert)

    result = analyze_ssl('example.com')

    assert result['has_ssl'] is True
    assert result['certificate_valid'] is True
    assert result['is_expired'] is False
    assert result['issuer'] == 'Example CA'
    assert result['issuer_common_name'] == 'Example CA Root'
    assert result['subject_common_name'] == 'example.com'
    assert 'www.example.com' in result['subject_alt_names']
    assert result['protocol_version'] == 'TLSv1.3'
    assert result['cipher'] == 'TLS_AES_256_GCM_SHA384'


@patch('backend.app.services.ssl_analyzer.socket.create_connection')
@patch('backend.app.services.ssl_analyzer.ssl.create_default_context')
def test_analyze_ssl_expired_certificate_is_flagged(mock_context_factory, mock_create_connection):
    fake_cert = {
        'issuer': ((('organizationName', 'Example CA'),),),
        'subject': ((('commonName', 'expired.example.com'),),),
        'notBefore': 'Jan  1 00:00:00 2000 GMT',
        'notAfter': 'Jan  1 00:00:00 2001 GMT',
        'subjectAltName': (),
    }
    _mock_tls_connection(mock_context_factory, mock_create_connection, fake_cert)

    result = analyze_ssl('expired.example.com')

    assert result['has_ssl'] is True
    assert result['is_expired'] is True
    assert result['certificate_valid'] is False


@patch('backend.app.services.ssl_analyzer.socket.create_connection')
def test_analyze_ssl_timeout_is_handled(mock_create_connection):
    mock_create_connection.side_effect = TimeoutError()

    result = analyze_ssl('slow.example.com')

    assert result['has_ssl'] is False
    assert 'timed out' in result['error']