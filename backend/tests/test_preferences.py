"""User preferences endpoint tests — skipped if PostgreSQL is not running."""

import uuid

import pytest
from sqlalchemy import text

from app.auth import create_access_token, hash_password
from app.database import SessionLocal, engine
from app.models.role import Role
from app.models.user import User


def _db_is_reachable() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


skip_no_db = pytest.mark.skipif(not _db_is_reachable(), reason="PostgreSQL not running")


def _make_student() -> tuple[str, str]:
    db = SessionLocal()
    try:
        role = db.query(Role).filter(Role.name == "student").first()
        user = User(
            email=f"pref_{uuid.uuid4().hex[:8]}@ufl.edu",
            display_name="Pref Tester",
            password_hash=hash_password("testpass"),
            role_id=role.id,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return str(user.id), create_access_token(str(user.id))
    finally:
        db.close()


@skip_no_db
def test_get_preferences_defaults(client):
    _, token = _make_student()
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.get("/api/preferences", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["dark_mode"] is False
    assert data["timezone"] == "America/New_York"
    assert data["notification_email"] is True
    assert data["notification_push"] is True


@skip_no_db
def test_update_dark_mode(client):
    _, token = _make_student()
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.patch(
        "/api/preferences",
        headers=headers,
        json={"dark_mode": True},
    )
    assert resp.status_code == 200
    assert resp.json()["dark_mode"] is True

    resp = client.get("/api/preferences", headers=headers)
    assert resp.json()["dark_mode"] is True


@skip_no_db
def test_update_timezone(client):
    _, token = _make_student()
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.patch(
        "/api/preferences",
        headers=headers,
        json={"timezone": "America/Chicago"},
    )
    assert resp.status_code == 200
    assert resp.json()["timezone"] == "America/Chicago"


@skip_no_db
def test_invalid_timezone_falls_back(client):
    _, token = _make_student()
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.patch(
        "/api/preferences",
        headers=headers,
        json={"timezone": "Mars/OlympusMons"},
    )
    assert resp.status_code == 200
    assert resp.json()["timezone"] == "America/New_York"


@skip_no_db
def test_preferences_require_auth(client):
    resp = client.get("/api/preferences")
    assert resp.status_code == 401
