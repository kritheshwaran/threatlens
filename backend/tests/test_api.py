from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_root():
    response = client.get('/')
    assert response.status_code == 200
    assert response.json()['message'] == 'ThreatLens backend is running'


def test_scan_status_get():
    response = client.get('/api/scan/')
    assert response.status_code == 200
    assert response.json() == {'status': 'idle'}


def test_scan_post_returns_full_result():
    response = client.post('/api/scan/', json={'url': 'https://example.com'})
    assert response.status_code == 200
    body = response.json()
    assert body['url'] == 'https://example.com'
    assert body['classification'] in ('safe', 'suspicious', 'malicious')
    assert 0.0 <= body['confidence'] <= 1.0
    assert 0.0 <= body['risk_score'] <= 100.0
    assert isinstance(body['features'], dict)
    assert isinstance(body['factors'], list)
    assert 'domain_intelligence' in body
    assert 'dns_intelligence' in body
    assert 'ssl_intelligence' in body
    assert 'whois' in body['domain_intelligence']
    assert set(body['dns_intelligence']['records'].keys()) == {'A', 'AAAA', 'MX', 'NS', 'TXT'}
    assert 'has_ssl' in body['ssl_intelligence']


def test_scan_post_flags_suspicious_url():
    response = client.post('/api/scan/', json={
        'url': 'http://secure-account-verify.tk/login?id=1'
    })
    assert response.status_code == 200
    body = response.json()
    assert body['classification'] in ('suspicious', 'malicious')


def test_scan_post_handles_ip_based_url():
    response = client.post('/api/scan/', json={'url': 'http://192.168.5.5/login'})
    assert response.status_code == 200
    body = response.json()
    assert body['domain_intelligence']['is_ip'] is True
    assert body['domain_intelligence']['whois']['available'] is False


def test_scan_post_rejects_empty_url():
    response = client.post('/api/scan/', json={'url': ''})
    assert response.status_code == 422


def test_scan_post_rejects_missing_url_field():
    response = client.post('/api/scan/', json={})
    assert response.status_code == 422