from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

VALID_CLASSIFICATIONS = {"SAFE", "LOW RISK", "MEDIUM RISK", "HIGH RISK", "CRITICAL"}


def test_root():
    response = client.get('/')
    assert response.status_code == 200
    assert response.json()['message'] == 'ThreatLens backend is running'


def test_scan_status_get():
    response = client.get('/api/scan/')
    assert response.status_code == 200
    assert response.json() == {'status': 'idle'}


def test_scan_post_returns_full_security_report():
    response = client.post('/api/scan/', json={'url': 'https://example.com'})
    assert response.status_code == 200
    body = response.json()

    assert body['url'] == 'https://example.com'
    assert body['classification'] in VALID_CLASSIFICATIONS
    assert 0.0 <= body['risk_score'] <= 100.0
    assert 0.0 <= body['confidence'] <= 1.0

    assert isinstance(body['reasons'], list)
    assert isinstance(body['positive_signals'], list)
    assert isinstance(body['negative_signals'], list)

    for key in ('url_analysis', 'domain_analysis', 'dns_analysis', 'ssl_analysis', 'threat_intelligence'):
        assert key in body

    assert 'features' in body['url_analysis']
    assert 'factors' in body['url_analysis']
    assert 'whois' in body['domain_analysis']
    assert set(body['dns_analysis']['records'].keys()) == {'A', 'AAAA', 'MX', 'NS', 'TXT'}
    assert 'has_ssl' in body['ssl_analysis']
    assert set(body['threat_intelligence'].keys()) >= {
        'virus_total', 'abuseipdb', 'openphish', 'phishtank', 'overall',
    }
    assert 'risk_breakdown' in body
    assert 'sub_scores' in body['risk_breakdown']


def test_scan_post_flags_suspicious_url_with_higher_score():
    safe = client.post('/api/scan/', json={'url': 'https://github.com/some/repo'}).json()
    suspicious = client.post('/api/scan/', json={
        'url': 'http://secure-account-verify-login.tk/billing?id=1'
    }).json()
    assert suspicious['risk_score'] > safe['risk_score']


def test_scan_post_handles_ip_based_url():
    response = client.post('/api/scan/', json={'url': 'http://192.168.5.5/login'})
    assert response.status_code == 200
    body = response.json()
    assert body['domain_analysis']['is_ip'] is True
    assert body['domain_analysis']['whois']['available'] is False


def test_scan_post_reasons_are_non_empty_for_risky_url():
    response = client.post('/api/scan/', json={
        'url': 'http://secure-paypal-update-billing.info/verify'
    })
    body = response.json()
    assert len(body['reasons']) > 0
    assert len(body['negative_signals']) > 0


def test_scan_post_rejects_empty_url():
    response = client.post('/api/scan/', json={'url': ''})
    assert response.status_code == 422


def test_scan_post_rejects_missing_url_field():
    response = client.post('/api/scan/', json={})
    assert response.status_code == 422