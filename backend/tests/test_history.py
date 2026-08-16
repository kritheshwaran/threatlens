def _register_and_login(client, email):
    response = client.post("/api/auth/register", json={"email": email, "password": "password12345"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_history_requires_authentication(client):
    response = client.get("/api/history/")
    assert response.status_code == 401


def test_history_empty_for_new_user(client, auth_headers):
    response = client.get("/api/history/", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_history_only_shows_own_scans(client):
    user_a_headers = _register_and_login(client, "alice@example.com")
    user_b_headers = _register_and_login(client, "bob@example.com")

    client.post("/api/scan/", json={"url": "https://alice-site.com"}, headers=user_a_headers)
    client.post("/api/scan/", json={"url": "https://bob-site.com"}, headers=user_b_headers)

    alice_history = client.get("/api/history/", headers=user_a_headers).json()
    bob_history = client.get("/api/history/", headers=user_b_headers).json()

    assert len(alice_history) == 1
    assert alice_history[0]["url"] == "https://alice-site.com"
    assert len(bob_history) == 1
    assert bob_history[0]["url"] == "https://bob-site.com"


def test_history_ordered_most_recent_first(client, auth_headers):
    client.post("/api/scan/", json={"url": "https://first.example.com"}, headers=auth_headers)
    client.post("/api/scan/", json={"url": "https://second.example.com"}, headers=auth_headers)

    history = client.get("/api/history/", headers=auth_headers).json()
    assert history[0]["url"] == "https://second.example.com"
    assert history[1]["url"] == "https://first.example.com"


def test_history_detail_returns_full_report(client, auth_headers):
    scan = client.post("/api/scan/", json={"url": "https://example.com"}, headers=auth_headers).json()
    response = client.get(f"/api/history/{scan['id']}", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == scan["id"]
    assert "reasons" in body
    assert "risk_breakdown" in body


def test_history_detail_404_for_unknown_scan(client, auth_headers):
    response = client.get("/api/history/999999", headers=auth_headers)
    assert response.status_code == 404


def test_history_detail_404_for_other_users_scan(client):
    user_a_headers = _register_and_login(client, "owner@example.com")
    user_b_headers = _register_and_login(client, "intruder@example.com")

    scan = client.post(
        "/api/scan/", json={"url": "https://private.example.com"}, headers=user_a_headers
    ).json()

    response = client.get(f"/api/history/{scan['id']}", headers=user_b_headers)
    assert response.status_code == 404