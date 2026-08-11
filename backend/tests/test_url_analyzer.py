from backend.app.services.url_analyzer import analyze_url
from backend.app.services.feature_extractor import extract_features, extract_features_dict, FEATURE_NAMES


def test_analyze_url_basic_structure():
    result = analyze_url('https://example.com')
    assert result['normalized_url'] == 'https://example.com'
    assert result['hostname'] == 'example.com'
    assert 'factors' in result
    assert isinstance(result['factors'], list)


def test_https_is_flagged_positive():
    result = analyze_url('https://example.com')
    labels = {f['label']: f['positive'] for f in result['factors']}
    assert labels.get('HTTPS enabled') is True


def test_no_https_is_flagged_negative():
    result = analyze_url('http://example.com')
    labels = {f['label']: f['positive'] for f in result['factors']}
    assert labels.get('No HTTPS encryption') is False


def test_ip_based_url_is_flagged():
    result = analyze_url('http://192.168.1.10/login')
    labels = [f['label'] for f in result['factors'] if not f['positive']]
    assert any('IP address' in label for label in labels)


def test_at_symbol_is_flagged():
    result = analyze_url('http://example.com@evil.com/login')
    labels = [f['label'] for f in result['factors'] if not f['positive']]
    assert any('@' in label for label in labels)


def test_suspicious_keywords_detected():
    result = analyze_url('https://secure-paypal-login-verify.info/account')
    labels = [f['label'] for f in result['factors'] if not f['positive']]
    assert any('Suspicious keyword' in label for label in labels)


def test_suspicious_tld_detected():
    result = analyze_url('https://freebies.tk/prize')
    labels = [f['label'] for f in result['factors'] if not f['positive']]
    assert any('top-level domain' in label for label in labels)


def test_feature_vector_length_matches_names():
    vector = extract_features('https://example.com/path?x=1')
    assert len(vector) == len(FEATURE_NAMES)
    assert all(isinstance(v, float) for v in vector)


def test_feature_dict_keys_match_names():
    features = extract_features_dict('https://example.com')
    assert set(features.keys()) == set(FEATURE_NAMES)


def test_entropy_is_higher_for_random_looking_url():
    low_entropy = extract_features_dict('https://example.com/')['entropy']
    high_entropy = extract_features_dict('https://xk29fj1lz8.tk/9f83jd')['entropy']
    assert high_entropy > low_entropy


def test_shortened_url_detected():
    features = extract_features_dict('http://bit.ly/abc123')
    assert features['is_shortened'] == 1.0