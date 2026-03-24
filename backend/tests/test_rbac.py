"""RBAC tests — skipped if PostgreSQL is not running."""

import uuid

import pytest
from sqlalchemy import text

from app.database import SessionLocal, engine
from app.models.role import Role
from app.models.user import User
from app.auth import hash_password, create_access_token


def _db_is_reachable() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


skip_no_db = pytest.mark.skipif(not _db_is_reachable(), reason="PostgreSQL not running")


def _create_user_with_role(role_name: str) -> str:
    """Create a user with the given role and return a JWT token."""
    db = SessionLocal()
    try:
        role = db.query(Role).filter(Role.name == role_name).first()
        user = User(
            email=f"{role_name}_{uuid.uuid4().hex[:8]}@ufl.edu",
            display_name=f"Test {role_name.title()}",
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
def test_admin_can_list_users(client):
    token = _create_user_with_role("admin")
    resp = client.get("/api/admin/users", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@skip_no_db
def test_student_cannot_list_users(client):
    token = _create_user_with_role("student")
    resp = client.get("/api/admin/users", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403


@skip_no_db
def test_ta_can_view_dashboard_stats(client):
    token = _create_user_with_role("ta")
    resp = client.get("/api/admin/dashboard-stats", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert "total_users" in data


@skip_no_db
def test_student_cannot_view_dashboard_stats(client):
    token = _create_user_with_role("student")
    resp = client.get("/api/admin/dashboard-stats", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403


@skip_no_db
def test_admin_can_list_roles(client):
    token = _create_user_with_role("admin")
    resp = client.get("/api/admin/roles", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    roles = [r["name"] for r in resp.json()]
    assert "student" in roles
    assert "ta" in roles
    assert "admin" in roles


@skip_no_db
def test_unauthenticated_cannot_access_admin(client):
    resp = client.get("/api/admin/users")
    assert resp.status_code == 401
