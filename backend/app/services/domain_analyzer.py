"""
Domain intelligence: registrable-domain extraction, subdomain detection,
and (best-effort) WHOIS registration data.

WHOIS lookups depend on reaching third-party WHOIS servers over the
network and are inherently best-effort: some registries rate-limit,
some TLDs have no public WHOIS, and some networks block port 43
entirely. This module NEVER raises out of analyze_domain() -- any
failure is reported as a structured "unavailable" result instead.
"""

import socket
from datetime import datetime, timezone
from urllib.parse import urlparse

from .feature_extractor import normalize_url, _is_ip_host

try:
    import whois as _whois_lib
except ImportError:  # pragma: no cover -- optional dependency guard
    _whois_lib = None

WHOIS_TIMEOUT_SECONDS = 6

# Not a full Public Suffix List -- a small set of common multi-part TLDs
# so registrable-domain extraction doesn't mangle e.g. "example.co.uk"
# into "co.uk". Anything not listed falls back to "last two labels".
MULTI_PART_TLDS = {
    "co.uk", "org.uk", "ac.uk", "gov.uk", "co.in", "co.jp", "co.nz",
    "co.za", "com.au", "com.br", "co.kr", "com.cn", "net.au", "org.au",
}


def get_registrable_domain(hostname: str) -> str:
    """
    Approximate the registrable domain, e.g. "mail.example.co.uk" -> "example.co.uk".
    Lightweight heuristic (see MULTI_PART_TLDS note above), not a full PSL parser.
    """
    if not hostname or _is_ip_host(hostname):
        return hostname or ""
    parts = hostname.split(".")
    if len(parts) <= 2:
        return hostname
    last_two = ".".join(parts[-2:])
    last_three = ".".join(parts[-3:])
    if last_two in MULTI_PART_TLDS and len(parts) >= 3:
        return last_three
    return last_two


def get_subdomain(hostname: str, registrable_domain: str) -> str:
    if not hostname or not registrable_domain or hostname == registrable_domain:
        return ""
    if hostname.endswith("." + registrable_domain):
        return hostname[: -(len(registrable_domain) + 1)]
    return ""


def _coerce_single(value):
    """WHOIS fields are sometimes lists (multiple matching records); take the first."""
    if isinstance(value, list):
        return value[0] if value else None
    return value


def _coerce_datetime(value):
    value = _coerce_single(value)
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value
    return None


def _to_str_list(value):
    if not value:
        return []
    if isinstance(value, (list, set, tuple)):
        return sorted({str(v).lower() for v in value if v})
    return [str(value).lower()]


def _lookup_whois(domain: str) -> dict:
    """
    Best-effort WHOIS lookup. Returns {"available": False, "error": ...}
    on any failure (timeout, no WHOIS server, parsing failure, blocked
    port 43, etc.) instead of raising.
    """
    if _whois_lib is None:
        return {"available": False, "error": "python-whois is not installed"}

    previous_timeout = socket.getdefaulttimeout()
    try:
        socket.setdefaulttimeout(WHOIS_TIMEOUT_SECONDS)
        record = _whois_lib.whois(domain)
    except Exception as exc:  # noqa: BLE001 -- WHOIS failures are numerous and best-effort
        return {"available": False, "error": f"{type(exc).__name__}: {exc}"}
    finally:
        socket.setdefaulttimeout(previous_timeout)

    if not record or not _coerce_single(getattr(record, "domain_name", None)):
        return {"available": False, "error": "No WHOIS record returned"}

    creation_date = _coerce_datetime(getattr(record, "creation_date", None))
    expiration_date = _coerce_datetime(getattr(record, "expiration_date", None))
    updated_date = _coerce_datetime(getattr(record, "updated_date", None))

    domain_age_days = None
    if creation_date:
        domain_age_days = (datetime.now(timezone.utc) - creation_date).days

    days_until_expiry = None
    if expiration_date:
        days_until_expiry = (expiration_date - datetime.now(timezone.utc)).days

    status = getattr(record, "status", None)
    if isinstance(status, list):
        status = [str(s) for s in status]
    elif status:
        status = [str(status)]
    else:
        status = []

    return {
        "available": True,
        "error": None,
        "registrar": _coerce_single(getattr(record, "registrar", None)),
        "creation_date": creation_date.isoformat() if creation_date else None,
        "expiration_date": expiration_date.isoformat() if expiration_date else None,
        "updated_date": updated_date.isoformat() if updated_date else None,
        "domain_age_days": domain_age_days,
        "days_until_expiry": days_until_expiry,
        "status": status,
        "name_servers": _to_str_list(getattr(record, "name_servers", None)),
    }


def analyze_domain(url: str) -> dict:
    """
    Return domain intelligence for a URL. Never raises -- WHOIS failures
    are reported inline via whois["available"] = False.

    {
        "hostname": "mail.example.com",
        "registrable_domain": "example.com",
        "subdomain": "mail",
        "is_ip": False,
        "whois": {"available": True, "registrar": "...", ...},
    }
    """
    normalized = normalize_url(url)
    hostname = urlparse(normalized).hostname or ""
    is_ip = _is_ip_host(hostname)

    if is_ip:
        return {
            "hostname": hostname,
            "registrable_domain": hostname,
            "subdomain": "",
            "is_ip": True,
            "whois": {"available": False, "error": "WHOIS is not applicable to IP addresses"},
        }

    if not hostname:
        return {
            "hostname": hostname,
            "registrable_domain": "",
            "subdomain": "",
            "is_ip": False,
            "whois": {"available": False, "error": "No hostname to look up"},
        }

    registrable_domain = get_registrable_domain(hostname)
    subdomain = get_subdomain(hostname, registrable_domain)
    whois_result = _lookup_whois(registrable_domain)

    return {
        "hostname": hostname,
        "registrable_domain": registrable_domain,
        "subdomain": subdomain,
        "is_ip": False,
        "whois": whois_result,
    }