from backend.app.services.explanation import explain, explain_risk


def test_explain_returns_expected_keys():
    result = explain(
        ml_confidence=0.1,
        factors=[],
        domain_intelligence=None,
        dns_intelligence=None,
        ssl_intelligence=None,
        threat_intelligence=None,
    )
    assert set(result.keys()) == {"reasons", "positive_signals", "negative_signals"}
    assert isinstance(result["reasons"], list)
    assert isinstance(result["positive_signals"], list)
    assert isinstance(result["negative_signals"], list)


def test_explain_ml_high_confidence_is_negative():
    result = explain(
        ml_confidence=0.9,
        factors=[],
        domain_intelligence=None,
        dns_intelligence=None,
        ssl_intelligence=None,
        threat_intelligence=None,
    )
    assert any("high confidence" in reason for reason in result["negative_signals"])


def test_explain_ml_low_confidence_is_positive():
    result = explain(
        ml_confidence=0.05,
        factors=[],
        domain_intelligence=None,
        dns_intelligence=None,
        ssl_intelligence=None,
        threat_intelligence=None,
    )
    assert any("low phishing probability" in reason for reason in result["positive_signals"])


def test_explain_domain_recently_registered_is_negative():
    result = explain(
        ml_confidence=0.1,
        factors=[],
        domain_intelligence={"is_ip": False, "whois": {"available": True, "domain_age_days": 5}},
        dns_intelligence=None,
        ssl_intelligence=None,
        threat_intelligence=None,
    )
    assert any("registered very recently" in reason for reason in result["negative_signals"])


def test_explain_domain_established_is_positive():
    result = explain(
        ml_confidence=0.1,
        factors=[],
        domain_intelligence={"is_ip": False, "whois": {"available": True, "domain_age_days": 3000}},
        dns_intelligence=None,
        ssl_intelligence=None,
        threat_intelligence=None,
    )
    assert any("established registration history" in reason for reason in result["positive_signals"])


def test_explain_missing_ssl_is_negative():
    result = explain(
        ml_confidence=0.1,
        factors=[],
        domain_intelligence=None,
        dns_intelligence=None,
        ssl_intelligence={"has_ssl": False},
        threat_intelligence=None,
    )
    assert any("SSL certificate is missing" in reason for reason in result["negative_signals"])


def test_explain_valid_ssl_is_positive():
    result = explain(
        ml_confidence=0.1,
        factors=[],
        domain_intelligence=None,
        dns_intelligence=None,
        ssl_intelligence={"has_ssl": True, "certificate_valid": True, "days_until_expiry": 200},
        threat_intelligence=None,
    )
    assert any("SSL certificate is valid" in reason for reason in result["positive_signals"])


def test_explain_expired_ssl_is_negative():
    result = explain(
        ml_confidence=0.1,
        factors=[],
        domain_intelligence=None,
        dns_intelligence=None,
        ssl_intelligence={"has_ssl": True, "certificate_valid": False, "is_expired": True},
        threat_intelligence=None,
    )
    assert any("expired" in reason for reason in result["negative_signals"])


def test_explain_dns_unresolved_is_negative():
    result = explain(
        ml_confidence=0.1,
        factors=[],
        domain_intelligence=None,
        dns_intelligence={"resolved": False},
        ssl_intelligence=None,
        threat_intelligence=None,
    )
    assert any("does not resolve" in reason for reason in result["negative_signals"])


def test_explain_threat_intelligence_malicious_is_negative():
    result = explain(
        ml_confidence=0.1,
        factors=[],
        domain_intelligence=None,
        dns_intelligence=None,
        ssl_intelligence=None,
        threat_intelligence={"overall": {"reputation": "malicious"}},
    )
    assert any("negative" in reason for reason in result["negative_signals"])


def test_explain_url_factors_pass_through():
    factors = [
        {"label": "HTTPS enabled", "positive": True},
        {"label": "Suspicious keyword detected", "positive": False},
    ]
    result = explain(
        ml_confidence=0.1,
        factors=factors,
        domain_intelligence=None,
        dns_intelligence=None,
        ssl_intelligence=None,
        threat_intelligence=None,
    )
    assert "HTTPS enabled" in result["positive_signals"]
    assert "Suspicious keyword detected" in result["negative_signals"]


def test_explain_reasons_combines_negative_then_positive():
    result = explain(
        ml_confidence=0.9,
        factors=[{"label": "positive thing", "positive": True}],
        domain_intelligence=None,
        dns_intelligence=None,
        ssl_intelligence=None,
        threat_intelligence=None,
    )
    assert result["reasons"] == result["negative_signals"] + result["positive_signals"]


def test_explain_risk_backward_compatible():
    assert explain_risk(90)["summary"] == "Critical risk"
    assert explain_risk(60)["summary"] == "High risk"
    assert explain_risk(40)["summary"] == "Medium risk"
    assert explain_risk(15)["summary"] == "Low risk"
    assert explain_risk(5)["summary"] == "Safe"