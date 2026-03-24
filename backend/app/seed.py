"""Seed the database with initial roles."""

from app.database import SessionLocal
from app.models.role import Role

ROLES = [
    {"name": "student", "description": "A registered student user"},
    {"name": "ta", "description": "A teaching assistant"},
    {"name": "admin", "description": "An administrator with full access"},
]


def seed_roles():
    db = SessionLocal()
    try:
        for role_data in ROLES:
            exists = db.query(Role).filter_by(name=role_data["name"]).first()
            if not exists:
                db.add(Role(**role_data))
                print(f"  Created role: {role_data['name']}")
            else:
                print(f"  Role already exists: {role_data['name']}")
        db.commit()
        print("Seeding complete.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_roles()
