"""Study sessions endpoint tests — skipped if PostgreSQL is not running."""

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

SESSION_PAYLOAD = {
    "title": "COP3530 Midterm Review",
    "location": "Library Room 204",
    "starts_at": "2026-05-01T14:00:00Z",
    "ends_at": "2026-05-01T16:00:00Z",
    "description": "Review graphs and trees",
}


def _make_student() -> tuple[str, str]:
    db = SessionLocal()
    try:
        role = db.query(Role).filter(Role.name == "student").first()
        user = User(
            email=f"sess_{uuid.uuid4().hex[:8]}@ufl.edu",
            display_name="Session Tester",
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
def test_create_and_list_session(client):
    _, token = _make_student()
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.post("/api/study-sessions", headers=headers, json=SESSION_PAYLOAD)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == SESSION_PAYLOAD["title"]
    assert data["location"] == SESSION_PAYLOAD["location"]
    session_id = data["id"]

    resp = client.get("/api/study-sessions", headers=headers)
    assert resp.status_code == 200
    ids = [s["id"] for s in resp.json()]
    assert session_id in ids


@skip_no_db
def test_get_single_session(client):
    _, token = _make_student()
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.post("/api/study-sessions", headers=headers, json=SESSION_PAYLOAD)
    session_id = resp.json()["id"]

    resp = client.get(f"/api/study-sessions/{session_id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["title"] == SESSION_PAYLOAD["title"]


@skip_no_db
def test_update_session(client):
    _, token = _make_student()
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.post("/api/study-sessions", headers=headers, json=SESSION_PAYLOAD)
    session_id = resp.json()["id"]

    resp = client.patch(
        f"/api/study-sessions/{session_id}",
        headers=headers,
        json={"title": "Updated Title", "location": "Zoom"},
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated Title"
    assert resp.json()["location"] == "Zoom"


@skip_no_db
def test_delete_session(client):
    _, token = _make_student()
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.post("/api/study-sessions", headers=headers, json=SESSION_PAYLOAD)
    session_id = resp.json()["id"]

    resp = client.delete(f"/api/study-sessions/{session_id}", headers=headers)
    assert resp.status_code == 204

    resp = client.get(f"/api/study-sessions/{session_id}", headers=headers)
    assert resp.status_code == 404


@skip_no_db
def test_invalid_time_range(client):
    _, token = _make_student()
    headers = {"Authorization": f"Bearer {token}"}

    bad = dict(SESSION_PAYLOAD, starts_at="2026-05-01T16:00:00Z", ends_at="2026-05-01T14:00:00Z")
    resp = client.post("/api/study-sessions", headers=headers, json=bad)
    assert resp.status_code == 422


@skip_no_db
def test_cannot_access_other_users_session(client):
    _, token_a = _make_student()
    _, token_b = _make_student()

    resp = client.post(
        "/api/study-sessions",
        headers={"Authorization": f"Bearer {token_a}"},
        json=SESSION_PAYLOAD,
    )
    session_id = resp.json()["id"]

    resp = client.get(
        f"/api/study-sessions/{session_id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert resp.status_code == 404


@skip_no_db
def test_sessions_require_auth(client):
    resp = client.get("/api/study-sessions")
    assert resp.status_code == 401
