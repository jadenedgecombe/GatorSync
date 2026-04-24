"""Assignment CRUD + auto-task-generation tests."""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import text

from app.auth import create_access_token, hash_password
from app.database import SessionLocal, engine
from app.models.role import Role
from app.models.task import Task
from app.models.user import User


def _db_is_reachable() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


skip_no_db = pytest.mark.skipif(not _db_is_reachable(), reason="PostgreSQL not running")


def _make_student_token() -> str:
    db = SessionLocal()
    try:
        role = db.query(Role).filter(Role.name == "student").first()
        user = User(
            email=f"asgn_{uuid.uuid4().hex[:8]}@ufl.edu",
            display_name="Asgn Tester",
            password_hash=hash_password("testpass"),
            role_id=role.id,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return create_access_token(str(user.id))
    finally:
        db.close()


@skip_no_db
def test_create_assignment_generates_single_task_for_small_work(client):
    token = _make_student_token()
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.post("/api/courses", headers=headers, json={"name": "Small Course"})
    course_id = resp.json()["id"]

    due = (datetime.now(timezone.utc) + timedelta(days=5)).isoformat()
    resp = client.post(
        "/api/assignments",
        headers=headers,
        json={
            "course_id": course_id,
            "title": "Quick HW",
            "due_date": due,
            "estimated_hours": 2,
        },
    )
    assert resp.status_code == 201
    assignment_id = resp.json()["id"]

    db = SessionLocal()
    try:
        tasks = db.query(Task).filter(Task.assignment_id == uuid.UUID(assignment_id)).all()
        assert len(tasks) == 1
        assert tasks[0].parent_task_id is None
    finally:
        db.close()


@skip_no_db
def test_create_large_assignment_splits_into_subtasks(client):
    token = _make_student_token()
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.post("/api/courses", headers=headers, json={"name": "Heavy Course"})
    course_id = resp.json()["id"]

    due = (datetime.now(timezone.utc) + timedelta(days=10)).isoformat()
    resp = client.post(
        "/api/assignments",
        headers=headers,
        json={
            "course_id": course_id,
            "title": "Big Project",
            "due_date": due,
            "estimated_hours": 9,
            "assignment_type": "project",
        },
    )
    assert resp.status_code == 201
    assignment_id = resp.json()["id"]

    db = SessionLocal()
    try:
        all_tasks = db.query(Task).filter(Task.assignment_id == uuid.UUID(assignment_id)).all()
        parents = [t for t in all_tasks if t.parent_task_id is None]
        subtasks = [t for t in all_tasks if t.parent_task_id is not None]
        assert len(parents) == 1
        assert len(subtasks) >= 2
    finally:
        db.close()


@skip_no_db
def test_list_assignments_filtered_by_course(client):
    token = _make_student_token()
    headers = {"Authorization": f"Bearer {token}"}

    c1 = client.post("/api/courses", headers=headers, json={"name": "C1"}).json()["id"]
    c2 = client.post("/api/courses", headers=headers, json={"name": "C2"}).json()["id"]

    client.post("/api/assignments", headers=headers, json={"course_id": c1, "title": "A1"})
    client.post("/api/assignments", headers=headers, json={"course_id": c2, "title": "A2"})

    resp = client.get(f"/api/assignments?course_id={c1}", headers=headers)
    titles = [a["title"] for a in resp.json()]
    assert "A1" in titles
    assert "A2" not in titles


@skip_no_db
def test_assignment_type_validation(client):
    token = _make_student_token()
    headers = {"Authorization": f"Bearer {token}"}

    c = client.post("/api/courses", headers=headers, json={"name": "C"}).json()["id"]
    resp = client.post(
        "/api/assignments",
        headers=headers,
        json={"course_id": c, "title": "Bad", "assignment_type": "bogus"},
    )
    assert resp.status_code == 422
