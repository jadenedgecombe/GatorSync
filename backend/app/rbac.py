"""Role-based access control dependencies.

Usage in any route:

    from app.rbac import require_role, require_any_role

    @router.get("/admin-only")
    def admin_panel(user = Depends(require_role("admin"))):
        ...

    @router.get("/staff-only")
    def staff_panel(user = Depends(require_any_role("ta", "admin"))):
        ...
"""

from fastapi import Depends, HTTPException, status

from app.auth import get_current_user
from app.models.user import User


def require_role(role_name: str):
    """Return a dependency that enforces a single required role."""

    def _check(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role.name != role_name:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This action requires the '{role_name}' role",
            )
        return current_user

    return _check


def require_any_role(*role_names: str):
    """Return a dependency that enforces any one of the listed roles."""

    def _check(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role.name not in role_names:
            allowed = ", ".join(role_names)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This action requires one of these roles: {allowed}",
            )
        return current_user

    return _check
