from backend.app.services.risk_engine import (
    SIGNAL_WEIGHTS,
    assess_risk,
    calculate_risk,
    classify,
    _score_dns,
    _score_domain,
    _score_ml,
    _score_ssl,
    _score_threat_intelligence,
    _score_url_heuristics,
)


# ---- Backward-compatible scaffold entry point ----

def test_calculate_risk():
    result = calculate_risk({'url_length': 10})
    assert 'risk_score' in result


def test_calculate_risk_handles_none_gracefully():
    result = calculate_risk(None)
    assert 'risk_score' in result


# ---- Weights ----

def test_signal_weights_sum_to_one():
    assert abs(sum(SIGNAL_WEIGHTS.values()) - 1.0) < 1e-9


# ---- Classification thresholds ----

def test_classify_safe():
    assert classify(0) == "SAFE"
    assert classify(9.99) == "SAFE"


def test_classify_low_risk():
    assert classify(10) == "LOW RISK"
    assert classify(29.99) == "LOW RISK"


def test_classify_medium_risk():
    assert classify(30) == "MEDIUM RISK"
    assert classify(54.99) == "MEDIUM RISK"


def test_classify_high_risk():
    assert classify(55) == "HIGH RISK"
    assert classify(79.99) == "HIGH RISK"


def test_classify_critical():
    assert classify(80) == "CRITICAL"
    assert classify(100) == "CRITICAL"


# ---- Individual sub-score functions ----

def test_score_ml_scales_with_confidence():
    assert _score_ml(0.0) == 0.0
    assert _score_ml(0.5) == 50.0
    assert _score_ml(1.0) == 100.0
    assert _score_ml(None) == 0.0


def test_score_url_heuristics_counts_negative_factors():
    factors = [
        {"label": "a", "positive": False},
        {"label": "b", "positive": False},
        {"label": "c", "positive": True},
    ]
    assert _score_url_heuristics(factors) == 30.0
    assert _score_url_heuristics([]) == 0.0


def test_score_domain_ip_address():
    assert _score_domain({"is_ip": True}) == 40.0


def test_score_domain_whois_unavailable():
    result = _score_domain({"is_ip": False, "whois": {"available": False}})
    assert result == 20.0


def test_score_domain_young_domain_scores_higher_than_old():
    young = _score_domain({"is_ip": False, "whois": {"available": True, "domain_age_days": 5}})
    old = _score_domain({"is_ip": False, "whois": {"available": True, "domain_age_days": 3000}})
    assert young > old
    assert old == 0.0


def test_score_dns_not_resolved_is_high_risk():
    assert _score_dns({"resolved": False}) == 70.0


def test_score_dns_resolved_with_ns_is_zero():
    dns_intel = {"resolved": True, "records": {"NS": {"records": ["ns1.example.com"]}}}
    assert _score_dns(dns_intel) == 0.0


def test_score_ssl_no_ssl_is_risky():
    assert _score_ssl({"has_ssl": False}) == 60.0


def test_score_ssl_invalid_cert_is_worse_than_no_ssl():
    invalid = _score_ssl({"has_ssl": True, "certificate_valid": False})
    missing = _score_ssl({"has_ssl": False})
    assert invalid > missing


def test_score_ssl_valid_cert_is_zero():
    assert _score_ssl({"has_ssl": True, "certificate_valid": True, "days_until_expiry": 200}) == 0.0


def test_score_threat_intelligence_malicious_is_highest():
    result = _score_threat_intelligence({"overall": {"reputation": "malicious"}})
    assert result == 90.0


def test_score_threat_intelligence_clean_is_zero():
    result = _score_threat_intelligence({"overall": {"reputation": "clean"}})
    assert result == 0.0


def test_score_threat_intelligence_unknown_is_small_penalty():
    result = _score_threat_intelligence({"overall": {"reputation": "unknown"}})
    assert 0.0 < result < 90.0


# ---- End-to-end assess_risk ----

def _clean_signals():
    return dict(
        ml_confidence=0.02,
        factors=[{"label": "HTTPS enabled", "positive": True}],
        domain_intelligence={
            "is_ip": False,
            "whois": {"available": True, "domain_age_days": 3000},
        },
        dns_intelligence={"resolved": True, "records": {"NS": {"records": ["ns1.example.com"]}}},
        ssl_intelligence={"has_ssl": True, "certificate_valid": True, "days_until_expiry": 200},
        threat_intelligence={"overall": {"reputation": "clean"}},
    )


def _malicious_signals():
    return dict(
        ml_confidence=0.98,
        factors=[
            {"label": "Suspicious keyword", "positive": False},
            {"label": "IP address used", "positive": False},
            {"label": "Hyphen in domain", "positive": False},
        ],
        domain_intelligence={"is_ip": True},
        dns_intelligence={"resolved": False},
        ssl_intelligence={"has_ssl": False},
        threat_intelligence={"overall": {"reputation": "malicious"}},
    )


def test_assess_risk_clean_url_is_low_score():
    result = assess_risk(**_clean_signals())
    assert result["risk_score"] < 20
    assert result["classification"] in ("SAFE", "LOW RISK")


def test_assess_risk_malicious_url_is_high_score():
    result = assess_risk(**_malicious_signals())
    assert result["risk_score"] > 70
    assert result["classification"] in ("HIGH RISK", "CRITICAL")


def test_assess_risk_is_deterministic():
    signals = _malicious_signals()
    result_a = assess_risk(**signals)
    result_b = assess_risk(**signals)
    assert result_a["risk_score"] == result_b["risk_score"]
    assert result_a["classification"] == result_b["classification"]


def test_assess_risk_score_is_bounded():
    result = assess_risk(**_malicious_signals())
    assert 0.0 <= result["risk_score"] <= 100.0


def test_assess_risk_confidence_reflects_data_completeness():
    full_data = assess_risk(**_clean_signals())
    no_data = assess_risk(
        ml_confidence=0.02,
        factors=[],
        domain_intelligence=None,
        dns_intelligence=None,
        ssl_intelligence=None,
        threat_intelligence=None,
    )
    assert full_data["confidence"] > no_data["confidence"]


def test_assess_risk_returns_sub_scores_for_every_signal():
    result = assess_risk(**_clean_signals())
    assert set(result["sub_scores"].keys()) == set(SIGNAL_WEIGHTS.keys())