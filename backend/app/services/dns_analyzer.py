"""
DNS intelligence: resolves A, AAAA, MX, NS, and TXT records for a
hostname. Each record type is resolved independently so a failure on
one (e.g. no MX records) never blocks the others. Never raises out of
analyze_dns() -- timeouts and lookup errors are reported inline.
"""

import dns.resolver
import dns.exception

DNS_TIMEOUT_SECONDS = 4
RECORD_TYPES = ["A", "AAAA", "MX", "NS", "TXT"]


def _make_resolver() -> "dns.resolver.Resolver":
    resolver = dns.resolver.Resolver()
    resolver.timeout = DNS_TIMEOUT_SECONDS
    resolver.lifetime = DNS_TIMEOUT_SECONDS
    return resolver


def _format_record(record_type: str, rdata) -> str:
    if record_type == "MX":
        return f"{rdata.preference} {rdata.exchange.to_text().rstrip('.')}"
    if record_type == "TXT":
        return "".join(
            part.decode("utf-8", errors="replace") if isinstance(part, bytes) else str(part)
            for part in rdata.strings
        )
    if record_type == "NS":
        return rdata.target.to_text().rstrip(".")
    return rdata.to_text()


def _resolve_one(resolver, hostname: str, record_type: str) -> dict:
    try:
        answers = resolver.resolve(hostname, record_type)
        records = [_format_record(record_type, r) for r in answers]
        return {"records": records, "error": None}
    except dns.resolver.NXDOMAIN:
        return {"records": [], "error": "domain does not exist"}
    except dns.resolver.NoAnswer:
        # Valid domain, just no records of this type -- not an error.
        return {"records": [], "error": None}
    except dns.exception.Timeout:
        return {"records": [], "error": "lookup timed out"}
    except Exception as exc:  # noqa: BLE001 -- DNS failures are numerous and best-effort
        return {"records": [], "error": f"{type(exc).__name__}: {exc}"}


def analyze_dns(hostname: str) -> dict:
    """
    Resolve A/AAAA/MX/NS/TXT records for `hostname`. Never raises.

    {
        "hostname": "example.com",
        "records": {
            "A": {"records": ["93.184.216.34"], "error": None},
            "AAAA": {"records": [], "error": None},
            "MX": {"records": ["10 mail.example.com"], "error": None},
            "NS": {"records": ["ns1.example.com"], "error": None},
            "TXT": {"records": ["v=spf1 ..."], "error": None},
        },
        "resolved": True,
    }
    """
    if not hostname:
        return {
            "hostname": hostname,
            "records": {rt: {"records": [], "error": "no hostname provided"} for rt in RECORD_TYPES},
            "resolved": False,
        }

    resolver = _make_resolver()
    results = {rt: _resolve_one(resolver, hostname, rt) for rt in RECORD_TYPES}
    resolved = bool(results["A"]["records"] or results["AAAA"]["records"])

    return {
        "hostname": hostname,
        "records": results,
        "resolved": resolved,
    }