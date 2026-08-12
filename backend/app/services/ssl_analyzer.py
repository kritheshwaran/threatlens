"""
SSL/TLS intelligence: performs a raw TLS handshake (no HTTP request is
issued and no page content is fetched) to retrieve the certificate a
host presents on port 443, then reports issuer, validity window, and
connection details. Never raises out of analyze_ssl() -- connection
and certificate errors are reported inline.
"""

import socket
import ssl
from datetime import datetime, timezone

SSL_TIMEOUT_SECONDS = 5
SSL_PORT = 443

CERT_DATE_FORMAT = "%b %d %H:%M:%S %Y %Z"


def _parse_cert_date(value):
    try:
        return datetime.strptime(value, CERT_DATE_FORMAT).replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return None


def _name_to_dict(name_tuple) -> dict:
    """Flatten a cert 'subject'/'issuer' tuple-of-tuples into a flat dict."""
    flat = {}
    for rdn in name_tuple or ():
        for key, value in rdn:
            flat[key] = value
    return flat


def analyze_ssl(hostname: str, port: int = SSL_PORT, timeout: int = SSL_TIMEOUT_SECONDS) -> dict:
    """
    Connect to hostname:port and inspect the presented TLS certificate.
    This performs ONLY a TLS handshake -- no HTTP GET, no page content
    is fetched, satisfying "do not crawl or execute the target website".

    On success:
        {
            "has_ssl": True,
            "certificate_valid": True,
            "is_expired": False,
            "is_not_yet_valid": False,
            "not_before": "2024-01-01T00:00:00+00:00",
            "not_after": "2030-01-01T00:00:00+00:00",
            "days_until_expiry": 1234,
            "issuer": "Example CA",
            "issuer_common_name": "Example CA Root",
            "subject_common_name": "example.com",
            "subject_alt_names": ["example.com", "www.example.com"],
            "protocol_version": "TLSv1.3",
            "cipher": "TLS_AES_256_GCM_SHA384",
            "error": None,
        }

    On failure: {"has_ssl": False, "error": "..."} (or has_ssl True with
    certificate_valid False if the handshake succeeded but the cert
    itself failed verification).
    """
    if not hostname:
        return {"has_ssl": False, "error": "no hostname provided"}

    context = ssl.create_default_context()
    try:
        with socket.create_connection((hostname, port), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                cipher_name, _, _ = ssock.cipher()
                protocol_version = ssock.version()
    except socket.gaierror as exc:
        return {"has_ssl": False, "error": f"DNS resolution failed: {exc}"}
    except socket.timeout:
        return {"has_ssl": False, "error": "connection timed out"}
    except ConnectionRefusedError:
        return {"has_ssl": False, "error": "connection refused (port closed)"}
    except ssl.SSLCertVerificationError as exc:
        return {
            "has_ssl": True,
            "certificate_valid": False,
            "error": f"certificate verification failed: {exc.verify_message}",
        }
    except ssl.SSLError as exc:
        return {"has_ssl": False, "error": f"TLS handshake failed: {exc}"}
    except OSError as exc:
        return {"has_ssl": False, "error": f"{type(exc).__name__}: {exc}"}

    not_before = _parse_cert_date(cert.get("notBefore"))
    not_after = _parse_cert_date(cert.get("notAfter"))
    now = datetime.now(timezone.utc)

    is_expired = bool(not_after and now > not_after)
    is_not_yet_valid = bool(not_before and now < not_before)
    certificate_valid = not is_expired and not is_not_yet_valid

    days_until_expiry = (not_after - now).days if not_after else None

    issuer = _name_to_dict(cert.get("issuer"))
    subject = _name_to_dict(cert.get("subject"))
    alt_names = [v for k, v in cert.get("subjectAltName", ()) if k == "DNS"]

    return {
        "has_ssl": True,
        "certificate_valid": certificate_valid,
        "is_expired": is_expired,
        "is_not_yet_valid": is_not_yet_valid,
        "not_before": not_before.isoformat() if not_before else None,
        "not_after": not_after.isoformat() if not_after else None,
        "days_until_expiry": days_until_expiry,
        "issuer": issuer.get("organizationName") or issuer.get("commonName"),
        "issuer_common_name": issuer.get("commonName"),
        "subject_common_name": subject.get("commonName"),
        "subject_alt_names": alt_names,
        "protocol_version": protocol_version,
        "cipher": cipher_name,
        "error": None,
    }