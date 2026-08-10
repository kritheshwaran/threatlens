from backend.app.services.risk_engine import calculate_risk

def test_calculate_risk():
    result = calculate_risk({'url_length': 10})
    assert 'risk_score' in result
