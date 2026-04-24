"""Course CRUD tests — skipped if PostgreSQL is not running."""

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
            email=f"course_{uuid.uuid4().hex[:8]}@ufl.edu",
            display_name="Course Tester",
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
def test_create_list_course(client):
    _, token = _make_student()
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.post(
        "/api/courses",
        headers=headers,
        json={"name": "Data Structures", "course_code": "COP 3530", "semester": "Spring 2026"},
    )
    assert resp.status_code == 201
    course_id = resp.json()["id"]

    resp = client.get("/api/courses", headers=headers)
    assert resp.status_code == 200
    codes = [c["course_code"] for c in resp.json()]
    assert "COP 3530" in codes

    resp = client.get(f"/api/courses/{course_id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Data Structures"


@skip_no_db
def test_update_and_delete_course(client):
    _, token = _make_student()
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.post("/api/courses", headers=headers, json={"name": "Temp"})
    course_id = resp.json()["id"]

    resp = client.patch(f"/api/courses/{course_id}", headers=headers, json={"instructor": "Dr. X"})
    assert resp.status_code == 200
    assert resp.json()["instructor"] == "Dr. X"

    resp = client.delete(f"/api/courses/{course_id}", headers=headers)
    assert resp.status_code == 204

    resp = client.get(f"/api/courses/{course_id}", headers=headers)
    assert resp.status_code == 404


@skip_no_db
def test_cannot_access_other_users_course(client):
    _, token_a = _make_student()
    _, token_b = _make_student()

    resp = client.post(
        "/api/courses", headers={"Authorization": f"Bearer {token_a}"}, json={"name": "Private"}
    )
    course_id = resp.json()["id"]

    resp = client.get(
        f"/api/courses/{course_id}", headers={"Authorization": f"Bearer {token_b}"}
    )
    assert resp.status_code == 404
