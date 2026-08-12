"""
Centralized risk engine: combines ML prediction, URL heuristics, domain
intelligence, DNS intelligence, SSL intelligence, and threat
intelligence into a single 0-100 risk score and a five-tier
classification.

SCORING LOGIC (documented, fully deterministic -- no randomness):

Each signal category produces its own 0-100 sub-score (see the
`_score_*` functions below), and the final risk score is a fixed
weighted sum of those sub-scores:

    Signal                Weight   What raises the sub-score
    --------------------   ------   ------------------------------------------------
    ml                     0.35     Higher phishing probability from the trained model
    url_heuristics         0.15     More negative factors from url_analyzer (Module 2)
    domain                 0.15     IP-hosted, WHOIS unavailable, or very young domain
    dns                    0.10     Domain doesn't resolve, or has no nameservers
    ssl                    0.15     No HTTPS, invalid/expired cert, or expiring soon
    threat_intelligence    0.10     Flagged as malicious by any external source

    risk_score = sum(weight * sub_score for each signal), clamped to [0, 100]

CLASSIFICATION (fixed thresholds on the final risk_score):

    score < 10             -> SAFE
    10  <= score < 30       -> LOW RISK
    30  <= score < 55       -> MEDIUM RISK
    55  <= score < 80       -> HIGH RISK
    score >= 80             -> CRITICAL

The engine is intentionally modular: each `_score_*` function takes
one signal's data and returns a single 0-100 number that is independent
of the others. Adding a new signal later means writing one more
`_score_*` function and adding one entry to SIGNAL_WEIGHTS + the call
list inside assess_risk() -- nothing else needs to change.
"""

SIGNAL_WEIGHTS = {
    "ml": 0.35,
    "url_heuristics": 0.15,
    "domain": 0.15,
    "dns": 0.10,
    "ssl": 0.15,
    "threat_intelligence": 0.10,
}

assert abs(sum(SIGNAL_WEIGHTS.values()) - 1.0) < 1e-9, "SIGNAL_WEIGHTS must sum to 1.0"

# (upper_bound_exclusive, label) -- first bound the score is strictly below wins.
CLASSIFICATION_THRESHOLDS = [
    (10, "SAFE"),
    (30, "LOW RISK"),
    (55, "MEDIUM RISK"),
    (80, "HIGH RISK"),
]
CRITICAL_LABEL = "CRITICAL"


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def _score_ml(ml_confidence: float) -> float:
    """Higher phishing probability from the trained classifier -> higher sub-score."""
    return _clamp((ml_confidence or 0.0) * 100)


def _score_url_heuristics(factors: list) -> float:
    """Each negative factor from Module 2's url_analyzer adds fixed points."""
    negative_count = sum(1 for f in (factors or []) if not f.get("positive", True))
    return _clamp(negative_count * 15)


def _score_domain(domain_intelligence: dict) -> float:
    if not domain_intelligence:
        return 50.0  # no data at all -- treat as moderately uncertain
    if domain_intelligence.get("is_ip"):
        return 40.0

    whois = domain_intelligence.get("whois") or {}
    if not whois.get("available"):
        return 20.0

    age_days = whois.get("domain_age_days")
    if age_days is None:
        return 15.0
    if age_days < 30:
        return 60.0
    if age_days < 180:
        return 30.0
    if age_days < 365:
        return 10.0
    return 0.0


def _score_dns(dns_intelligence: dict) -> float:
    if not dns_intelligence:
        return 50.0
    if not dns_intelligence.get("resolved"):
        return 70.0
    ns_records = dns_intelligence.get("records", {}).get("NS", {}).get("records", [])
    if not ns_records:
        return 20.0
    return 0.0


def _score_ssl(ssl_intelligence: dict) -> float:
    if not ssl_intelligence:
        return 50.0
    if not ssl_intelligence.get("has_ssl"):
        return 60.0
    if ssl_intelligence.get("certificate_valid") is False:
        return 80.0
    days_until_expiry = ssl_intelligence.get("days_until_expiry")
    if days_until_expiry is not None and days_until_expiry < 7:
        return 20.0
    return 0.0


def _score_threat_intelligence(threat_intelligence: dict) -> float:
    if not threat_intelligence:
        return 10.0
    reputation = (threat_intelligence.get("overall") or {}).get("reputation", "unknown")
    if reputation == "malicious":
        return 90.0
    if reputation == "unknown":
        return 10.0
    return 0.0  # "clean"


def _score_data_completeness(
    domain_intelligence: dict, dns_intelligence: dict, ssl_intelligence: dict, threat_intelligence: dict
) -> float:
    """
    How much real signal backs this assessment, as a 0-1 fraction.
    This becomes the API's `confidence` field -- distinct from
    risk_score, it measures data availability, not maliciousness.
    """
    checks = [1.0]  # ML prediction is always available
    checks.append(1.0 if (domain_intelligence or {}).get("whois", {}).get("available") else 0.0)
    checks.append(1.0 if (dns_intelligence or {}).get("resolved") else 0.0)
    checks.append(1.0 if (ssl_intelligence or {}).get("has_ssl") else 0.0)

    ti = threat_intelligence or {}
    sources_checked = ti.get("sources_checked", 0)
    sources_available = ti.get("sources_available", 0)
    checks.append(sources_available / sources_checked if sources_checked else 0.0)

    return round(sum(checks) / len(checks), 2)


def classify(risk_score: float) -> str:
    for threshold, label in CLASSIFICATION_THRESHOLDS:
        if risk_score < threshold:
            return label
    return CRITICAL_LABEL


def assess_risk(
    ml_confidence: float,
    factors: list,
    domain_intelligence: dict,
    dns_intelligence: dict,
    ssl_intelligence: dict,
    threat_intelligence: dict,
) -> dict:
    """
    Combine every signal into a final risk score + classification.
    Purely deterministic: the same inputs always produce the same
    output -- no randomness anywhere in this function.
    """
    sub_scores = {
        "ml": _score_ml(ml_confidence),
        "url_heuristics": _score_url_heuristics(factors),
        "domain": _score_domain(domain_intelligence),
        "dns": _score_dns(dns_intelligence),
        "ssl": _score_ssl(ssl_intelligence),
        "threat_intelligence": _score_threat_intelligence(threat_intelligence),
    }

    weighted_sum = sum(SIGNAL_WEIGHTS[name] * score for name, score in sub_scores.items())
    risk_score = round(_clamp(weighted_sum), 2)
    classification = classify(risk_score)

    confidence = _score_data_completeness(
        domain_intelligence, dns_intelligence, ssl_intelligence, threat_intelligence
    )

    return {
        "risk_score": risk_score,
        "classification": classification,
        "confidence": confidence,
        "sub_scores": sub_scores,
        "weights": dict(SIGNAL_WEIGHTS),
    }


def calculate_risk(features: dict) -> dict:
    """
    Backward-compatible entry point matching the original project
    scaffold's `calculate_risk(features_dict)` signature. Prefer
    assess_risk() directly for the full Module 4 pipeline -- this
    wrapper exists only so any earlier code importing `calculate_risk`
    keeps working unchanged.
    """
    features = features or {}
    return assess_risk(
        ml_confidence=features.get("ml_confidence", 0.0),
        factors=features.get("factors", []),
        domain_intelligence=features.get("domain_intelligence"),
        dns_intelligence=features.get("dns_intelligence"),
        ssl_intelligence=features.get("ssl_intelligence"),
        threat_intelligence=features.get("threat_intelligence"),
    )