"""
Canonical URL feature extraction for ThreatLens.

This module is the SINGLE source of truth for turning a raw URL string
into a numeric feature vector. Both the training pipeline (ml/scripts/*)
and the live prediction path (backend/app/ml/predictor.py) import
FEATURE_NAMES and extract_features() from here, so there is no
train/serve skew.
"""

import math
import re
from urllib.parse import urlparse

# Ordered list of feature names. Order matters -- it defines vector position.
FEATURE_NAMES = [
    "url_length",
    "hostname_length",
    "path_length",
    "num_dots",
    "num_hyphens",
    "num_underscores",
    "num_slashes",
    "num_digits",
    "num_special_chars",
    "num_subdomains",
    "num_query_params",
    "is_ip",
    "has_at_symbol",
    "has_https",
    "num_suspicious_keywords",
    "entropy",
    "has_double_slash_redirect",
    "has_encoding",
    "digit_ratio",
    "is_shortened",
    "domain_has_hyphen",
    "tld_suspicious",
    "path_depth",
]

SUSPICIOUS_KEYWORDS = [
    "login", "verify", "secure", "account", "update", "banking",
    "confirm", "signin", "webscr", "billing", "password", "wallet",
    "suspend", "unlock", "authenticate", "recover", "invoice",
]

SUSPICIOUS_TLDS = {
    "tk", "ml", "ga", "cf", "gq", "xyz", "top", "info", "click", "work",
}

KNOWN_SHORTENERS = {
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd",
    "buff.ly", "rebrand.ly", "cutt.ly",
}

_IP_PATTERN = re.compile(
    r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$"
)


def _shannon_entropy(s: str) -> float:
    if not s:
        return 0.0
    freq = {}
    for ch in s:
        freq[ch] = freq.get(ch, 0) + 1
    length = len(s)
    entropy = 0.0
    for count in freq.values():
        p = count / length
        entropy -= p * math.log2(p)
    return entropy


def _is_ip_host(hostname: str) -> bool:
    if not hostname:
        return False
    return bool(_IP_PATTERN.match(hostname))


def _count_subdomains(hostname: str) -> int:
    if not hostname or _is_ip_host(hostname):
        return 0
    parts = hostname.split(".")
    if len(parts) <= 2:
        return 0
    return len(parts) - 2


def _get_tld(hostname: str) -> str:
    if not hostname or _is_ip_host(hostname):
        return ""
    parts = hostname.split(".")
    return parts[-1].lower() if parts else ""


def normalize_url(url: str) -> str:
    url = url.strip()
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.\-]*://", url):
        url = "http://" + url
    return url


def extract_raw_features(url: str) -> dict:
    """Parse a URL and return a dict of raw (human-interpretable) features."""
    normalized = normalize_url(url)
    parsed = urlparse(normalized)

    hostname = parsed.hostname or ""
    path = parsed.path or ""
    query = parsed.query or ""

    num_query_params = len([p for p in query.split("&") if p]) if query else 0

    special_chars = re.findall(r"[^a-zA-Z0-9./:\-_]", normalized)

    lower_url = normalized.lower()
    matched_keywords = [kw for kw in SUSPICIOUS_KEYWORDS if kw in lower_url]

    domain_registered_part = ".".join(hostname.split(".")[-2:]) if hostname else ""

    return {
        "normalized_url": normalized,
        "hostname": hostname,
        "path": path,
        "query": query,
        "url_length": len(normalized),
        "hostname_length": len(hostname),
        "path_length": len(path),
        "num_dots": normalized.count("."),
        "num_hyphens": normalized.count("-"),
        "num_underscores": normalized.count("_"),
        "num_slashes": normalized.count("/"),
        "num_digits": sum(c.isdigit() for c in normalized),
        "num_special_chars": len(special_chars),
        "num_subdomains": _count_subdomains(hostname),
        "num_query_params": num_query_params,
        "is_ip": _is_ip_host(hostname),
        "has_at_symbol": "@" in normalized,
        "has_https": parsed.scheme == "https",
        "matched_keywords": matched_keywords,
        "num_suspicious_keywords": len(matched_keywords),
        "entropy": round(_shannon_entropy(normalized), 4),
        "has_double_slash_redirect": "//" in (path + query),
        "has_encoding": "%" in normalized,
        "digit_ratio": round(
            sum(c.isdigit() for c in normalized) / len(normalized), 4
        ) if normalized else 0.0,
        "is_shortened": domain_registered_part in KNOWN_SHORTENERS,
        "domain_has_hyphen": "-" in hostname,
        "tld_suspicious": _get_tld(hostname) in SUSPICIOUS_TLDS,
        "path_depth": len([seg for seg in path.split("/") if seg]),
    }


def extract_features(url: str) -> list:
    """Return an ordered numeric feature vector matching FEATURE_NAMES."""
    raw = extract_raw_features(url)
    vector = []
    for name in FEATURE_NAMES:
        value = raw[name]
        if isinstance(value, bool):
            vector.append(1.0 if value else 0.0)
        else:
            vector.append(float(value))
    return vector


def extract_features_dict(url: str) -> dict:
    """Return {feature_name: value} for the numeric vector only (JSON-friendly)."""
    raw = extract_raw_features(url)
    return {name: raw[name] for name in FEATURE_NAMES}