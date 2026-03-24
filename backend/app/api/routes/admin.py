"""Admin-only routes for user and role management."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.role import Role
from app.models.user import User
from app.rbac import require_any_role, require_role

router = APIRouter()


class UserSummary(BaseModel):
    id: str
    email: str
    display_name: str
    role: str

    model_config = {"from_attributes": True}


class RoleSummary(BaseModel):
    id: str
    name: str
    description: str | None

    model_config = {"from_attributes": True}


# ---- Admin only ----

@router.get("/users", response_model=list[UserSummary])
def list_users(
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_role("admin")),
):
    """List all registered users. Admin only."""
    users = db.query(User).all()
    return [
        UserSummary(
            id=str(u.id),
            email=u.email,
            display_name=u.display_name,
            role=u.role.name,
        )
        for u in users
    ]


@router.get("/roles", response_model=list[RoleSummary])
def list_roles(
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_role("admin")),
):
    """List all roles. Admin only."""
    roles = db.query(Role).all()
    return [
        RoleSummary(id=str(r.id), name=r.name, description=r.description)
        for r in roles
    ]


# ---- TA or Admin ----

@router.get("/dashboard-stats")
def admin_dashboard_stats(
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_any_role("ta", "admin")),
):
    """Overview stats for staff. TA or Admin only."""
    total_users = db.query(User).count()
    roles = db.query(Role).all()
    role_counts = {}
    for role in roles:
        role_counts[role.name] = db.query(User).filter(User.role_id == role.id).count()

    return {
        "total_users": total_users,
        "users_by_role": role_counts,
    }
