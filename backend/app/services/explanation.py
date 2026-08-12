"""
Explainability engine: turns each signal's raw data into plain-language
reasons, split into positive (risk-reducing) and negative
(risk-increasing) indicators. This is what lets the API answer
"why did this URL get this score?" instead of just returning a number.
"""


def _domain_reasons(domain_intelligence: dict) -> tuple:
    positive, negative = [], []
    if not domain_intelligence:
        return positive, negative

    if domain_intelligence.get("is_ip"):
        negative.append("URL uses a raw IP address instead of a domain name")
        return positive, negative

    whois = domain_intelligence.get("whois") or {}
    if not whois.get("available"):
        negative.append("Domain registration data (WHOIS) is unavailable")
    else:
        age_days = whois.get("domain_age_days")
        if age_days is not None:
            if age_days < 30:
                negative.append(f"Domain was registered very recently ({age_days} days ago)")
            elif age_days < 180:
                negative.append(f"Domain is relatively new ({age_days} days old)")
            else:
                positive.append(f"Domain has an established registration history ({age_days} days old)")
        days_until_expiry = whois.get("days_until_expiry")
        if days_until_expiry is not None and days_until_expiry < 30:
            negative.append("Domain registration expires soon")

    return positive, negative


def _dns_reasons(dns_intelligence: dict) -> tuple:
    positive, negative = [], []
    if not dns_intelligence:
        return positive, negative

    if not dns_intelligence.get("resolved"):
        negative.append("Domain does not resolve to any IP address")
        return positive, negative

    positive.append("Domain resolves to a valid IP address")

    ns_records = dns_intelligence.get("records", {}).get("NS", {}).get("records", [])
    if not ns_records:
        negative.append("Domain has no nameserver (NS) records")
    else:
        positive.append("Domain has properly configured nameservers")

    return positive, negative


def _ssl_reasons(ssl_intelligence: dict) -> tuple:
    positive, negative = [], []
    if not ssl_intelligence:
        return positive, negative

    if not ssl_intelligence.get("has_ssl"):
        negative.append("SSL certificate is missing or unreachable on port 443")
        return positive, negative

    if ssl_intelligence.get("certificate_valid") is False:
        if ssl_intelligence.get("is_expired"):
            negative.append("SSL certificate has expired")
        else:
            negative.append("SSL certificate failed validation")
    else:
        positive.append("SSL certificate is valid")
        days_until_expiry = ssl_intelligence.get("days_until_expiry")
        if days_until_expiry is not None and days_until_expiry < 7:
            negative.append("SSL certificate expires within a week")

    return positive, negative


def _threat_intelligence_reasons(threat_intelligence: dict) -> tuple:
    positive, negative = [], []
    if not threat_intelligence:
        return positive, negative

    overall = threat_intelligence.get("overall") or {}
    reputation = overall.get("reputation", "unknown")

    if reputation == "malicious":
        negative.append("Threat intelligence reputation is negative (flagged by external sources)")
    elif reputation == "clean":
        positive.append("No external threat intelligence source flagged this URL")
    else:
        negative.append("Threat intelligence sources are unavailable or not configured")

    return positive, negative


def _url_heuristic_reasons(factors: list) -> tuple:
    positive, negative = [], []
    for factor in factors or []:
        label = factor.get("label")
        if not label:
            continue
        if factor.get("positive"):
            positive.append(label)
        else:
            negative.append(label)
    return positive, negative


def _ml_reason(ml_confidence: float) -> tuple:
    positive, negative = [], []
    if ml_confidence is None:
        return positive, negative
    percent = round(ml_confidence * 100)
    if ml_confidence >= 0.7:
        negative.append(f"ML model predicts phishing with high confidence ({percent}%)")
    elif ml_confidence >= 0.35:
        negative.append(f"ML model flags this URL as moderately suspicious ({percent}%)")
    else:
        positive.append(f"ML model predicts a low phishing probability ({percent}%)")
    return positive, negative


def explain(
    ml_confidence: float,
    factors: list,
    domain_intelligence: dict,
    dns_intelligence: dict,
    ssl_intelligence: dict,
    threat_intelligence: dict,
) -> dict:
    """
    Build the full list of reasons behind a risk score.

    Returns:
        {
            "reasons": [...],            # negative signals first, then positive
            "positive_signals": [...],
            "negative_signals": [...],
        }
    """
    positive_signals: list = []
    negative_signals: list = []

    for builder, arg in (
        (_ml_reason, ml_confidence),
        (_url_heuristic_reasons, factors),
        (_domain_reasons, domain_intelligence),
        (_dns_reasons, dns_intelligence),
        (_ssl_reasons, ssl_intelligence),
        (_threat_intelligence_reasons, threat_intelligence),
    ):
        pos, neg = builder(arg)
        positive_signals.extend(pos)
        negative_signals.extend(neg)

    reasons = negative_signals + positive_signals

    return {
        "reasons": reasons,
        "positive_signals": positive_signals,
        "negative_signals": negative_signals,
    }


def explain_risk(score: float) -> dict:
    """
    Backward-compatible entry point matching the original scaffold's
    `explain_risk(score)` signature. Prefer explain() directly for the
    full Module 4 pipeline.
    """
    if score >= 80:
        summary = "Critical risk"
    elif score >= 55:
        summary = "High risk"
    elif score >= 30:
        summary = "Medium risk"
    elif score >= 10:
        summary = "Low risk"
    else:
        summary = "Safe"
    return {"summary": summary}