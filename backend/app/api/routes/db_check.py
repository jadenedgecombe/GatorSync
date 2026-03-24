from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.role import Role

router = APIRouter()


@router.get("/db-check")
def db_check(db: Session = Depends(get_db)):
    """Verify database connection and list seeded roles."""
    db.execute(text("SELECT 1"))
    roles = db.query(Role).all()
    return {
        "status": "connected",
        "database": "PostgreSQL",
        "roles": [r.name for r in roles],
    }
