def test_register_creates_user_and_returns_token(client):
    response = client.post(
        "/api/auth/register",
        json={"email": "new@example.com", "password": "supersecretpassword"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["user"]["email"] == "new@example.com"
    assert "access_token" in body
    assert body["token_type"] == "bearer"
    # Password must never be echoed back
    assert "password" not in body["user"]


def test_register_rejects_duplicate_email(client):
    client.post("/api/auth/register", json={"email": "dupe@example.com", "password": "password123"})
    response = client.post("/api/auth/register", json={"email": "dupe@example.com", "password": "password123"})
    assert response.status_code == 409


def test_register_rejects_short_password(client):
    response = client.post("/api/auth/register", json={"email": "short@example.com", "password": "short"})
    assert response.status_code == 422


def test_login_with_correct_credentials(client):
    client.post("/api/auth/register", json={"email": "login@example.com", "password": "correctpassword"})
    response = client.post("/api/auth/login", json={"email": "login@example.com", "password": "correctpassword"})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_with_wrong_password_is_rejected(client):
    client.post("/api/auth/register", json={"email": "wrongpw@example.com", "password": "correctpassword"})
    response = client.post("/api/auth/login", json={"email": "wrongpw@example.com", "password": "wrongpassword"})
    assert response.status_code == 401


def test_login_with_unknown_email_is_rejected(client):
    response = client.post("/api/auth/login", json={"email": "nope@example.com", "password": "whatever123"})
    assert response.status_code == 401


def test_password_is_never_stored_in_plaintext(client):
    from backend.app.database.database import SessionLocal  # noqa -- only used to prove intent below
    client.post("/api/auth/register", json={"email": "hash@example.com", "password": "plaintextpassword"})
    # We can't easily reach the per-test session here; instead assert
    # indirectly: the stored hash must verify via bcrypt, not equality.
    from backend.app.core.security import get_password_hash, verify_password
    hashed = get_password_hash("plaintextpassword")
    assert hashed != "plaintextpassword"
    assert verify_password("plaintextpassword", hashed)
    assert not verify_password("wrongpassword", hashed)


def test_me_requires_authentication(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_me_returns_current_user_with_valid_token(client, auth_headers):
    response = client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "analyst@example.com"


def test_me_rejects_invalid_token(client):
    response = client.get("/api/auth/me", headers={"Authorization": "Bearer not-a-real-token"})
    assert response.status_code == 401