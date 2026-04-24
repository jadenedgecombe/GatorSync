"""Seed the database with initial roles and template courses + assignments."""

from datetime import datetime, timedelta, timezone

from app.database import SessionLocal
from app.models.assignment import Assignment
from app.models.course import Course
from app.models.role import Role

ROLES = [
    {"name": "student", "description": "A registered student user"},
    {"name": "ta", "description": "A teaching assistant"},
    {"name": "admin", "description": "An administrator with full access"},
]


TEMPLATE_COURSES = [
    {
        "name": "Data Structures & Algorithms",
        "course_code": "COP 3530",
        "semester": "Spring 2026",
        "instructor": "Prof. Davis",
        "pattern": "weekly_hw_plus_midterms",
    },
    {
        "name": "Computer Organization",
        "course_code": "CDA 3101",
        "semester": "Spring 2026",
        "instructor": "Prof. Kim",
        "pattern": "biweekly_hw_plus_project",
    },
    {
        "name": "Software Engineering",
        "course_code": "CEN 3031",
        "semester": "Spring 2026",
        "instructor": "Prof. Patel",
        "pattern": "sprints",
    },
    {
        "name": "Professional Writing",
        "course_code": "ENC 3246",
        "semester": "Spring 2026",
        "instructor": "Prof. Reyes",
        "pattern": "weekly_drafts",
    },
    {
        "name": "Engineering Statistics",
        "course_code": "STA 3032",
        "semester": "Spring 2026",
        "instructor": "Prof. Nguyen",
        "pattern": "weekly_hw_plus_midterms",
    },
    {
        "name": "Operating Systems",
        "course_code": "COP 4600",
        "semester": "Fall 2026",
        "instructor": "Prof. Singh",
        "pattern": "biweekly_hw_plus_project",
    },
    {
        "name": "Database Management Systems",
        "course_code": "COP 4720",
        "semester": "Fall 2026",
        "instructor": "Prof. Ortiz",
        "pattern": "weekly_hw_plus_midterms",
    },
    {
        "name": "Intro to Artificial Intelligence",
        "course_code": "CAP 4630",
        "semester": "Fall 2026",
        "instructor": "Prof. Chen",
        "pattern": "biweekly_hw_plus_project",
    },
    {
        "name": "Technical Writing",
        "course_code": "ENC 3254",
        "semester": "Fall 2026",
        "instructor": "Prof. Hall",
        "pattern": "weekly_drafts",
    },
]


def _due(start: datetime, days_offset: int) -> datetime:
    return (start + timedelta(days=days_offset)).replace(hour=23, minute=59)


def _generate_assignments(course_start: datetime, pattern: str) -> list[dict]:
    items: list[dict] = []

    if pattern == "weekly_hw_plus_midterms":
        for i in range(1, 13):
            items.append({
                "title": f"Homework {i}",
                "description": f"Weekly problem set {i}",
                "due_date": _due(course_start, i * 7),
                "assignment_type": "homework",
                "estimated_hours": 3,
                "weight": 3.0,
            })
        items.append({
            "title": "Midterm Exam",
            "description": "In-class midterm covering the first half of the course",
            "due_date": _due(course_start, 45),
            "assignment_type": "exam",
            "estimated_hours": 8,
            "weight": 20.0,
        })
        items.append({
            "title": "Final Exam",
            "description": "Cumulative final exam",
            "due_date": _due(course_start, 105),
            "assignment_type": "exam",
            "estimated_hours": 10,
            "weight": 30.0,
        })

    elif pattern == "biweekly_hw_plus_project":
        for i in range(1, 7):
            items.append({
                "title": f"Homework {i}",
                "description": f"Homework {i}",
                "due_date": _due(course_start, i * 14),
                "assignment_type": "homework",
                "estimated_hours": 4,
                "weight": 5.0,
            })
        items.append({
            "title": "Course Project Proposal",
            "description": "One-page project proposal",
            "due_date": _due(course_start, 21),
            "assignment_type": "project",
            "estimated_hours": 3,
            "weight": 5.0,
        })
        items.append({
            "title": "Course Project Milestone",
            "description": "Midterm milestone demo",
            "due_date": _due(course_start, 56),
            "assignment_type": "project",
            "estimated_hours": 8,
            "weight": 10.0,
        })
        items.append({
            "title": "Course Project Final Report",
            "description": "Final report + demo",
            "due_date": _due(course_start, 100),
            "assignment_type": "project",
            "estimated_hours": 12,
            "weight": 20.0,
        })
        items.append({
            "title": "Midterm Exam",
            "description": "Written midterm",
            "due_date": _due(course_start, 49),
            "assignment_type": "exam",
            "estimated_hours": 8,
            "weight": 15.0,
        })

    elif pattern == "sprints":
        for i in range(1, 6):
            items.append({
                "title": f"Sprint {i} Deliverable",
                "description": f"Sprint {i} deliverable with retrospective",
                "due_date": _due(course_start, 14 + (i - 1) * 14),
                "assignment_type": "project",
                "estimated_hours": 10,
                "weight": 10.0,
            })
        items.append({
            "title": "Final Presentation",
            "description": "Team final presentation",
            "due_date": _due(course_start, 105),
            "assignment_type": "project",
            "estimated_hours": 6,
            "weight": 15.0,
        })

    elif pattern == "weekly_drafts":
        for i in range(1, 13):
            items.append({
                "title": f"Reading Response {i}",
                "description": f"Short reading response {i}",
                "due_date": _due(course_start, i * 7 + 2),
                "assignment_type": "reading",
                "estimated_hours": 2,
                "weight": 2.0,
            })
        items.append({
            "title": "Peer Review Draft",
            "description": "Draft for peer review workshop",
            "due_date": _due(course_start, 60),
            "assignment_type": "homework",
            "estimated_hours": 5,
            "weight": 10.0,
        })
        items.append({
            "title": "Final Portfolio",
            "description": "Revised writing portfolio",
            "due_date": _due(course_start, 105),
            "assignment_type": "project",
            "estimated_hours": 8,
            "weight": 20.0,
        })

    return items


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
    finally:
        db.close()


def seed_templates():
    db = SessionLocal()
    try:
        total_assignments = 0
        for tpl in TEMPLATE_COURSES:
            existing = (
                db.query(Course)
                .filter(
                    Course.course_code == tpl["course_code"],
                    Course.semester == tpl["semester"],
                    Course.is_template.is_(True),
                )
                .first()
            )
            if existing:
                print(f"  Template already exists: {tpl['course_code']} — {tpl['semester']}")
                continue

            course_start = datetime(2026, 1, 6, tzinfo=timezone.utc)
            if tpl["semester"].startswith("Fall"):
                course_start = datetime(2026, 8, 25, tzinfo=timezone.utc)

            course = Course(
                user_id=None,
                is_template=True,
                name=tpl["name"],
                course_code=tpl["course_code"],
                semester=tpl["semester"],
                instructor=tpl["instructor"],
                semester_start=course_start.date(),
                semester_end=(course_start + timedelta(days=112)).date(),
            )
            db.add(course)
            db.flush()

            assignments = _generate_assignments(course_start, tpl["pattern"])
            for a in assignments:
                db.add(Assignment(course_id=course.id, **a))
            total_assignments += len(assignments)
            print(f"  Created template: {tpl['course_code']} — {len(assignments)} assignments")

        db.commit()
        print(f"Seeded {total_assignments} template assignments.")
    finally:
        db.close()


def seed_all():
    seed_roles()
    seed_templates()
    print("Seeding complete.")


if __name__ == "__main__":
    seed_all()
