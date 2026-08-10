from backend.app.services.url_analyzer import analyze_url

def test_analyze_url():
    result = analyze_url('http://example.com')
    assert result['status'] == 'ok'
