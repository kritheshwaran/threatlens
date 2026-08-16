"""
Shared pytest fixtures for Module 5: a fresh SQLite database per test
(via FastAPI's dependency_overrides), so auth/scan/history/analytics
tests never touch a real PostgreSQL instance or leak state between
tests. Production still uses PostgreSQL (see .env.example) -- this is
purely a test-time substitution of the same SQLAlchemy interface.
"""

import os

os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-pytest-only-not-for-production-use")
os.environ.setdefault("DATABASE_URL", "sqlite:////tmp/threatlens_test_startup.db")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.database.database import Base, get_db
from backend.app.main import app

TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture()
def client():
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=__import__("sqlalchemy").pool.StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def auth_headers(client):
    """Registers a fresh user and returns Authorization headers for them."""
    response = client.post(
        "/api/auth/register",
        json={"email": "analyst@example.com", "password": "correct-horse-battery-staple"},
    )
    assert response.status_code == 201, response.text
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}