def test_analytics_requires_authentication(client):
    response = client.get("/api/analytics/")
    assert response.status_code == 401


def test_analytics_empty_for_new_user(client, auth_headers):
    response = client.get("/api/analytics/", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["summary"]["total_scans"] == 0
    assert body["summary"]["safe_scans"] == 0
    assert body["summary"]["threats_detected"] == 0
    assert len(body["threat_trend"]) == 8
    assert body["classification_breakdown"] == []
    assert body["recent_scans"] == []


def test_analytics_reflects_scans(client, auth_headers):
    client.post("/api/scan/", json={"url": "https://example.com"}, headers=auth_headers)
    client.post("/api/scan/", json={"url": "http://192.168.5.5/login-verify"}, headers=auth_headers)

    response = client.get("/api/analytics/", headers=auth_headers)
    body = response.json()

    assert body["summary"]["total_scans"] == 2
    assert body["summary"]["scans_today"] == 2
    assert len(body["recent_scans"]) == 2
    assert sum(item["value"] for item in body["classification_breakdown"]) == 2


def test_analytics_trend_has_eight_days_summing_to_total_scans_within_window(client, auth_headers):
    client.post("/api/scan/", json={"url": "https://example.com"}, headers=auth_headers)

    response = client.get("/api/analytics/", headers=auth_headers)
    body = response.json()

    trend_total = sum(day["safe"] + day["suspicious"] + day["malicious"] for day in body["threat_trend"])
    assert trend_total == 1


def test_analytics_scoped_per_user(client):
    a = client.post(
        "/api/auth/register", json={"email": "a2@example.com", "password": "password12345"}
    ).json()
    b = client.post(
        "/api/auth/register", json={"email": "b2@example.com", "password": "password12345"}
    ).json()
    headers_a = {"Authorization": f"Bearer {a['access_token']}"}
    headers_b = {"Authorization": f"Bearer {b['access_token']}"}

    client.post("/api/scan/", json={"url": "https://example.com"}, headers=headers_a)

    analytics_a = client.get("/api/analytics/", headers=headers_a).json()
    analytics_b = client.get("/api/analytics/", headers=headers_b).json()

    assert analytics_a["summary"]["total_scans"] == 1
    assert analytics_b["summary"]["total_scans"] == 0