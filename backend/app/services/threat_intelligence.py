"""
Threat intelligence: reputation lookups against external services
(VirusTotal, AbuseIPDB, OpenPhish, PhishTank).

Every check is opt-in via environment variables and every function is
best-effort: missing API keys, network failures, and rate limits are
all reported as a structured "unavailable" result rather than raised.
No API key is ever hardcoded -- all credentials come from the
environment:

    VIRUSTOTAL_API_KEY   -- required for VirusTotal domain reputation
    ABUSEIPDB_API_KEY    -- required for AbuseIPDB IP reputation
    PHISHTANK_API_KEY    -- optional for PhishTank (raises rate limit)
    OPENPHISH_FEED_URL   -- optional override for the OpenPhish feed URL
"""

import os
import time

import requests

VIRUSTOTAL_API_KEY = os.environ.get("VIRUSTOTAL_API_KEY", "")
ABUSEIPDB_API_KEY = os.environ.get("ABUSEIPDB_API_KEY", "")
PHISHTANK_API_KEY = os.environ.get("PHISHTANK_API_KEY", "")
OPENPHISH_FEED_URL = os.environ.get("OPENPHISH_FEED_URL", "https://openphish.com/feed.txt")

REQUEST_TIMEOUT_SECONDS = 6

# Small in-memory TTL cache for the OpenPhish feed -- it's a few
# thousand lines refreshed periodically upstream, so re-fetching it on
# every single scan would be wasteful and slow.
_OPENPHISH_CACHE = {"fetched_at": 0.0, "urls": set()}
_OPENPHISH_CACHE_TTL_SECONDS = 15 * 60


def _unavailable(reason: str) -> dict:
    return {"available": False, "error": reason}


def check_virustotal_domain(domain: str) -> dict:
    """
    Domain reputation via VirusTotal's /domains/{domain} endpoint.
    Requires VIRUSTOTAL_API_KEY.
    """
    if not domain:
        return _unavailable("no domain provided")
    if not VIRUSTOTAL_API_KEY:
        return _unavailable("VIRUSTOTAL_API_KEY is not configured")

    try:
        response = requests.get(
            f"https://www.virustotal.com/api/v3/domains/{domain}",
            headers={"x-apikey": VIRUSTOTAL_API_KEY},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except requests.RequestException as exc:
        return _unavailable(f"request failed: {exc}")

    if response.status_code == 404:
        return {
            "available": True,
            "error": None,
            "found": False,
            "malicious_count": 0,
            "suspicious_count": 0,
            "harmless_count": 0,
            "reputation": None,
        }
    if response.status_code != 200:
        return _unavailable(f"unexpected status {response.status_code}")

    try:
        payload = response.json()
        stats = payload["data"]["attributes"]["last_analysis_stats"]
        reputation = payload["data"]["attributes"].get("reputation")
    except (KeyError, ValueError, TypeError) as exc:
        return _unavailable(f"unexpected response shape: {exc}")

    return {
        "available": True,
        "error": None,
        "found": True,
        "malicious_count": stats.get("malicious", 0),
        "suspicious_count": stats.get("suspicious", 0),
        "harmless_count": stats.get("harmless", 0),
        "reputation": reputation,
    }


def check_abuseipdb(ip_address: str) -> dict:
    """IP reputation via AbuseIPDB. Requires ABUSEIPDB_API_KEY."""
    if not ip_address:
        return _unavailable("no IP address to check")
    if not ABUSEIPDB_API_KEY:
        return _unavailable("ABUSEIPDB_API_KEY is not configured")

    try:
        response = requests.get(
            "https://api.abuseipdb.com/api/v2/check",
            params={"ipAddress": ip_address, "maxAgeInDays": 90},
            headers={"Key": ABUSEIPDB_API_KEY, "Accept": "application/json"},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except requests.RequestException as exc:
        return _unavailable(f"request failed: {exc}")

    if response.status_code != 200:
        return _unavailable(f"unexpected status {response.status_code}")

    try:
        data = response.json()["data"]
    except (KeyError, ValueError, TypeError) as exc:
        return _unavailable(f"unexpected response shape: {exc}")

    return {
        "available": True,
        "error": None,
        "ip_address": ip_address,
        "abuse_confidence_score": data.get("abuseConfidenceScore", 0),
        "total_reports": data.get("totalReports", 0),
        "country_code": data.get("countryCode"),
        "is_whitelisted": data.get("isWhitelisted"),
    }


def _fetch_openphish_feed() -> set:
    now = time.time()
    if now - _OPENPHISH_CACHE["fetched_at"] < _OPENPHISH_CACHE_TTL_SECONDS and _OPENPHISH_CACHE["urls"]:
        return _OPENPHISH_CACHE["urls"]

    response = requests.get(OPENPHISH_FEED_URL, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    urls = {line.strip() for line in response.text.splitlines() if line.strip()}
    _OPENPHISH_CACHE["urls"] = urls
    _OPENPHISH_CACHE["fetched_at"] = now
    return urls


def check_openphish(url: str) -> dict:
    """
    Checks whether `url` appears in the public OpenPhish feed.
    No API key required.
    """
    if not url:
        return _unavailable("no url provided")

    try:
        feed = _fetch_openphish_feed()
    except requests.RequestException as exc:
        return _unavailable(f"feed fetch failed: {exc}")

    listed = url in feed or url.rstrip("/") in feed
    return {
        "available": True,
        "error": None,
        "listed": listed,
        "feed_size": len(feed),
    }


def check_phishtank(url: str) -> dict:
    """
    Checks a URL against PhishTank. PHISHTANK_API_KEY is optional --
    anonymous lookups work but are more tightly rate-limited.
    """
    if not url:
        return _unavailable("no url provided")

    payload = {"url": url, "format": "json"}
    if PHISHTANK_API_KEY:
        payload["app_key"] = PHISHTANK_API_KEY

    try:
        response = requests.post(
            "https://checkurl.phishtank.com/checkurl/",
            data=payload,
            headers={"User-Agent": "ThreatLens/1.0"},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except requests.RequestException as exc:
        return _unavailable(f"request failed: {exc}")

    if response.status_code != 200:
        return _unavailable(f"unexpected status {response.status_code}")

    try:
        results = response.json()["results"]
    except (KeyError, ValueError, TypeError) as exc:
        return _unavailable(f"unexpected response shape: {exc}")

    return {
        "available": True,
        "error": None,
        "in_database": bool(results.get("in_database")),
        "verified": bool(results.get("verified")),
        "valid": bool(results.get("valid")),
    }


def _pick_ipv4(dns_intelligence: dict) -> str:
    if not dns_intelligence:
        return ""
    a_records = dns_intelligence.get("records", {}).get("A", {}).get("records", [])
    return a_records[0] if a_records else ""


def analyze_threat_intelligence(url: str, hostname: str, dns_intelligence: dict = None) -> dict:
    """
    Run all configured threat-intel checks and summarize them into one
    structured result. Never raises -- each individual check is
    isolated and best-effort.

    {
        "virus_total": {...},
        "abuseipdb": {...},
        "openphish": {...},
        "phishtank": {...},
        "sources_checked": 4,
        "sources_available": 1,
        "overall": {
            "reputation": "clean" | "suspicious" | "malicious" | "unknown",
            "malicious_votes": 0,
            "total_votes": 1,
        },
    }
    """
    ip_address = _pick_ipv4(dns_intelligence or {})

    virus_total = check_virustotal_domain(hostname)
    abuseipdb = check_abuseipdb(ip_address)
    openphish = check_openphish(url)
    phishtank = check_phishtank(url)

    sources = {
        "virus_total": virus_total,
        "abuseipdb": abuseipdb,
        "openphish": openphish,
        "phishtank": phishtank,
    }
    available_sources = [s for s in sources.values() if s.get("available")]

    malicious_votes = 0
    if virus_total.get("available") and (virus_total.get("malicious_count") or 0) > 0:
        malicious_votes += 1
    if abuseipdb.get("available") and (abuseipdb.get("abuse_confidence_score") or 0) >= 50:
        malicious_votes += 1
    if openphish.get("available") and openphish.get("listed"):
        malicious_votes += 1
    if phishtank.get("available") and phishtank.get("in_database") and phishtank.get("verified"):
        malicious_votes += 1

    if not available_sources:
        overall_reputation = "unknown"
    elif malicious_votes > 0:
        overall_reputation = "malicious"
    else:
        overall_reputation = "clean"

    return {
        **sources,
        "sources_checked": len(sources),
        "sources_available": len(available_sources),
        "overall": {
            "reputation": overall_reputation,
            "malicious_votes": malicious_votes,
            "total_votes": len(available_sources),
        },
    }