from unittest.mock import MagicMock, patch

import requests

from backend.app.services import threat_intelligence as ti


def setup_function(_):
    # Reset the module-level OpenPhish cache between tests so one test
    # can't leak cached feed data into another.
    ti._OPENPHISH_CACHE["fetched_at"] = 0.0
    ti._OPENPHISH_CACHE["urls"] = set()


# ---- Missing API key handling (graceful, no network call attempted) ----

def test_check_virustotal_domain_missing_api_key(monkeypatch):
    monkeypatch.setattr(ti, "VIRUSTOTAL_API_KEY", "")
    result = ti.check_virustotal_domain("example.com")
    assert result["available"] is False
    assert "VIRUSTOTAL_API_KEY" in result["error"]


def test_check_abuseipdb_missing_api_key(monkeypatch):
    monkeypatch.setattr(ti, "ABUSEIPDB_API_KEY", "")
    result = ti.check_abuseipdb("1.2.3.4")
    assert result["available"] is False
    assert "ABUSEIPDB_API_KEY" in result["error"]


def test_check_abuseipdb_no_ip():
    result = ti.check_abuseipdb("")
    assert result["available"] is False


# ---- Successful lookups (mocked HTTP) ----

@patch("backend.app.services.threat_intelligence.requests.get")
def test_check_virustotal_domain_success(mock_get, monkeypatch):
    monkeypatch.setattr(ti, "VIRUSTOTAL_API_KEY", "fake-key")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "attributes": {
                "last_analysis_stats": {"malicious": 5, "suspicious": 2, "harmless": 60},
                "reputation": -10,
            }
        }
    }
    mock_get.return_value = mock_response

    result = ti.check_virustotal_domain("evil.example.com")

    assert result["available"] is True
    assert result["malicious_count"] == 5
    assert result["reputation"] == -10


@patch("backend.app.services.threat_intelligence.requests.get")
def test_check_virustotal_domain_not_found(mock_get, monkeypatch):
    monkeypatch.setattr(ti, "VIRUSTOTAL_API_KEY", "fake-key")
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    result = ti.check_virustotal_domain("neverseen.example.com")

    assert result["available"] is True
    assert result["found"] is False


@patch("backend.app.services.threat_intelligence.requests.get")
def test_check_abuseipdb_success(mock_get, monkeypatch):
    monkeypatch.setattr(ti, "ABUSEIPDB_API_KEY", "fake-key")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {"abuseConfidenceScore": 87, "totalReports": 42, "countryCode": "US", "isWhitelisted": False}
    }
    mock_get.return_value = mock_response

    result = ti.check_abuseipdb("1.2.3.4")

    assert result["available"] is True
    assert result["abuse_confidence_score"] == 87


@patch("backend.app.services.threat_intelligence.requests.get")
def test_check_openphish_listed(mock_get):
    mock_response = MagicMock()
    mock_response.text = "http://evil.example.com/login\nhttp://another-bad-one.example.com\n"
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    result = ti.check_openphish("http://evil.example.com/login")

    assert result["available"] is True
    assert result["listed"] is True
    assert result["feed_size"] == 2


@patch("backend.app.services.threat_intelligence.requests.get")
def test_check_openphish_not_listed(mock_get):
    mock_response = MagicMock()
    mock_response.text = "http://evil.example.com/login\n"
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    result = ti.check_openphish("https://example.com")

    assert result["available"] is True
    assert result["listed"] is False


@patch("backend.app.services.threat_intelligence.requests.post")
def test_check_phishtank_in_database(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "results": {"in_database": True, "verified": True, "valid": True}
    }
    mock_post.return_value = mock_response

    result = ti.check_phishtank("http://evil.example.com/login")

    assert result["available"] is True
    assert result["in_database"] is True
    assert result["verified"] is True


# ---- Network / error handling ----

@patch("backend.app.services.threat_intelligence.requests.get")
def test_check_virustotal_domain_request_exception(mock_get, monkeypatch):
    monkeypatch.setattr(ti, "VIRUSTOTAL_API_KEY", "fake-key")
    mock_get.side_effect = requests.exceptions.Timeout("timed out")

    result = ti.check_virustotal_domain("example.com")

    assert result["available"] is False
    assert "timed out" in result["error"]


@patch("backend.app.services.threat_intelligence.requests.get")
def test_check_openphish_feed_fetch_failure(mock_get):
    mock_get.side_effect = requests.exceptions.ConnectionError("network unreachable")

    result = ti.check_openphish("https://example.com")

    assert result["available"] is False
    assert "feed fetch failed" in result["error"]


# ---- Aggregate function ----

@patch("backend.app.services.threat_intelligence.check_phishtank")
@patch("backend.app.services.threat_intelligence.check_openphish")
@patch("backend.app.services.threat_intelligence.check_abuseipdb")
@patch("backend.app.services.threat_intelligence.check_virustotal_domain")
def test_analyze_threat_intelligence_all_unavailable_is_unknown(
    mock_vt, mock_abuse, mock_op, mock_pt
):
    mock_vt.return_value = {"available": False, "error": "no key"}
    mock_abuse.return_value = {"available": False, "error": "no key"}
    mock_op.return_value = {"available": False, "error": "network error"}
    mock_pt.return_value = {"available": False, "error": "network error"}

    result = ti.analyze_threat_intelligence("https://example.com", "example.com", {})

    assert result["sources_available"] == 0
    assert result["overall"]["reputation"] == "unknown"


@patch("backend.app.services.threat_intelligence.check_phishtank")
@patch("backend.app.services.threat_intelligence.check_openphish")
@patch("backend.app.services.threat_intelligence.check_abuseipdb")
@patch("backend.app.services.threat_intelligence.check_virustotal_domain")
def test_analyze_threat_intelligence_flags_malicious(mock_vt, mock_abuse, mock_op, mock_pt):
    mock_vt.return_value = {"available": True, "malicious_count": 12}
    mock_abuse.return_value = {"available": False, "error": "no ip"}
    mock_op.return_value = {"available": True, "listed": False}
    mock_pt.return_value = {"available": True, "in_database": False, "verified": False}

    result = ti.analyze_threat_intelligence("https://evil.example.com", "evil.example.com", {})

    assert result["overall"]["reputation"] == "malicious"
    assert result["overall"]["malicious_votes"] == 1


@patch("backend.app.services.threat_intelligence.check_phishtank")
@patch("backend.app.services.threat_intelligence.check_openphish")
@patch("backend.app.services.threat_intelligence.check_abuseipdb")
@patch("backend.app.services.threat_intelligence.check_virustotal_domain")
def test_analyze_threat_intelligence_all_clean(mock_vt, mock_abuse, mock_op, mock_pt):
    mock_vt.return_value = {"available": True, "malicious_count": 0}
    mock_abuse.return_value = {"available": True, "abuse_confidence_score": 0}
    mock_op.return_value = {"available": True, "listed": False}
    mock_pt.return_value = {"available": True, "in_database": False, "verified": False}

    result = ti.analyze_threat_intelligence("https://example.com", "example.com", {})

    assert result["overall"]["reputation"] == "clean"
    assert result["overall"]["malicious_votes"] == 0


def test_pick_ipv4_uses_first_a_record():
    dns_intelligence = {"records": {"A": {"records": ["1.2.3.4", "5.6.7.8"]}}}
    assert ti._pick_ipv4(dns_intelligence) == "1.2.3.4"


def test_pick_ipv4_no_a_records():
    assert ti._pick_ipv4({"records": {"A": {"records": []}}}) == ""
    assert ti._pick_ipv4({}) == ""