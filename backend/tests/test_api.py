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


def test_scan_post_flags_suspicious_url():
    response = client.post('/api/scan/', json={
        'url': 'http://secure-account-verify.tk/login?id=1'
    })
    assert response.status_code == 200
    body = response.json()
    assert body['classification'] in ('suspicious', 'malicious')


def test_scan_post_rejects_empty_url():
    response = client.post('/api/scan/', json={'url': ''})
    assert response.status_code == 422


def test_scan_post_rejects_missing_url_field():
    response = client.post('/api/scan/', json={})
    assert response.status_code == 422