from backend.app.ml.predictor import predict_url
from backend.app.ml.model import ThreatModel


def test_model_loads_without_error():
    model = ThreatModel.get()
    assert model.model_name in ('logistic_regression', 'random_forest')
    assert 0.0 <= model.metrics['f1'] <= 1.0


def test_predict_url_response_shape():
    result = predict_url('https://example.com')
    assert set(result.keys()) == {
        'url', 'normalized_url', 'classification', 'confidence',
        'risk_score', 'model_name', 'features', 'factors',
    }
    assert result['classification'] in ('safe', 'suspicious', 'malicious')
    assert 0.0 <= result['confidence'] <= 1.0
    assert 0.0 <= result['risk_score'] <= 100.0


def test_predict_url_flags_obvious_phishing_pattern():
    result = predict_url('http://192.168.5.5/paypal-secure-login-verify')
    assert result['classification'] in ('suspicious', 'malicious')
    assert result['risk_score'] > 30


def test_predict_url_flags_clean_url_as_low_risk():
    result = predict_url('https://github.com/some/repo')
    assert result['risk_score'] < 50


def test_predict_url_is_deterministic():
    result_a = predict_url('https://example.com/path')
    result_b = predict_url('https://example.com/path')
    assert result_a['risk_score'] == result_b['risk_score']
    assert result_a['classification'] == result_b['classification']