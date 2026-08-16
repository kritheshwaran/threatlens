"""
Module 5 scan tests: authentication requirement + persistence to the
database. (Module 4's ML/risk-engine tests already cover the report
content itself -- these focus on the auth + DB layer added here.)
"""


def test_scan_requires_authentication(client):
    response = client.post("/api/scan/", json={"url": "https://example.com"})
    assert response.status_code == 401


def test_scan_persists_and_returns_full_report(client, auth_headers):
    response = client.post("/api/scan/", json={"url": "https://example.com"}, headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body["id"], int)
    assert body["url"] == "https://example.com"
    assert body["classification"] in ("SAFE", "LOW RISK", "MEDIUM RISK", "HIGH RISK", "CRITICAL")
    assert "created_at" in body
    assert "domain_analysis" in body
    assert "threat_intelligence" in body


def test_scan_shows_up_in_history(client, auth_headers):
    client.post("/api/scan/", json={"url": "https://example.com"}, headers=auth_headers)
    response = client.get("/api/history/", headers=auth_headers)
    assert response.status_code == 200
    history = response.json()
    assert len(history) == 1
    assert history[0]["url"] == "https://example.com"


def test_scan_rejects_empty_url(client, auth_headers):
    response = client.post("/api/scan/", json={"url": ""}, headers=auth_headers)
    assert response.status_code == 422