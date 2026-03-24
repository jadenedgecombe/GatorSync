"""Auth endpoint tests — skipped if PostgreSQL is not running."""

import uuid

import pytest
from sqlalchemy import text

from app.database import engine


def _db_is_reachable() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


skip_no_db = pytest.mark.skipif(not _db_is_reachable(), reason="PostgreSQL not running")


def _unique_email():
    return f"test_{uuid.uuid4().hex[:8]}@ufl.edu"


@skip_no_db
def test_register_and_login(client):
    email = _unique_email()

    # Register
    resp = client.post("/api/auth/register", json={
        "email": email,
        "display_name": "Test User",
        "password": "securepass123",
    })
    assert resp.status_code == 201
    token = resp.json()["access_token"]
    assert token

    # Get current user
    resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == email
    assert data["role"] == "student"

    # Login with same credentials
    resp = client.post("/api/auth/login", json={
        "email": email,
        "password": "securepass123",
    })
    assert resp.status_code == 200
    assert resp.json()["access_token"]


@skip_no_db
def test_register_duplicate_email(client):
    email = _unique_email()
    client.post("/api/auth/register", json={
        "email": email,
        "display_name": "First",
        "password": "pass123",
    })
    resp = client.post("/api/auth/register", json={
        "email": email,
        "display_name": "Second",
        "password": "pass456",
    })
    assert resp.status_code == 409


@skip_no_db
def test_login_wrong_password(client):
    email = _unique_email()
    client.post("/api/auth/register", json={
        "email": email,
        "display_name": "Wrong",
        "password": "correctpass",
    })
    resp = client.post("/api/auth/login", json={
        "email": email,
        "password": "wrongpass",
    })
    assert resp.status_code == 401


@skip_no_db
def test_me_without_token(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401
