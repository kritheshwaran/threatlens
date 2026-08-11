"""
URL analysis: turns raw extracted features into human-readable
"factors" (label + positive/negative) for display in scan reports.

Uses backend.app.services.feature_extractor as the single source of
numeric truth -- this module only adds interpretation on top.
"""

from .feature_extractor import extract_raw_features


def analyze_url(url: str) -> dict:
    """
    Analyze a URL and return raw features plus a human-readable
    factor list, e.g.:
        {
            "normalized_url": "https://example.com",
            "hostname": "example.com",
            "raw_features": {...},
            "factors": [{"label": "HTTPS enabled", "positive": True}, ...],
        }
    """
    raw = extract_raw_features(url)
    factors = _build_factors(raw)

    return {
        "normalized_url": raw["normalized_url"],
        "hostname": raw["hostname"],
        "raw_features": raw,
        "factors": factors,
    }


def _build_factors(raw: dict) -> list:
    factors = []

    if raw["has_https"]:
        factors.append({"label": "HTTPS enabled", "positive": True})
    else:
        factors.append({"label": "No HTTPS encryption", "positive": False})

    if raw["is_ip"]:
        factors.append({"label": "IP address used instead of domain name", "positive": False})

    if raw["has_at_symbol"]:
        factors.append({"label": "'@' symbol present in URL", "positive": False})

    if raw["is_shortened"]:
        factors.append({"label": "URL shortening service detected", "positive": False})

    if raw["num_subdomains"] >= 3:
        factors.append({"label": "Excessive subdomain nesting", "positive": False})

    if raw["num_suspicious_keywords"] > 0:
        factors.append({
            "label": f"Suspicious keyword(s) detected: {', '.join(raw['matched_keywords'][:3])}",
            "positive": False,
        })

    if raw["tld_suspicious"]:
        factors.append({"label": "Domain uses a commonly-abused top-level domain", "positive": False})

    if raw["domain_has_hyphen"]:
        factors.append({"label": "Hyphen in domain name (common in impersonation)", "positive": False})

    if raw["has_encoding"]:
        factors.append({"label": "URL contains percent-encoded characters", "positive": False})

    if raw["has_double_slash_redirect"]:
        factors.append({"label": "Unusual redirect pattern in path", "positive": False})

    if raw["entropy"] > 4.5:
        factors.append({"label": "High randomness in URL structure", "positive": False})

    if raw["url_length"] > 75:
        factors.append({"label": "Unusually long URL", "positive": False})

    # Positive signals when nothing else was flagged for that dimension
    if not raw["is_ip"] and not raw["domain_has_hyphen"] and raw["num_subdomains"] < 3:
        factors.append({"label": "Conventional domain structure", "positive": True})

    if raw["num_suspicious_keywords"] == 0:
        factors.append({"label": "No suspicious keywords detected", "positive": True})

    return factors