"""Course template routes.

- Students: list available templates, import a template into their workspace.
- TAs/Admins: publish a new template or convert one of their courses into a template.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.routes.assignments import _autogenerate_tasks
from app.auth import get_current_user
from app.database import get_db
from app.models.assignment import Assignment
from app.models.course import Course
from app.models.user import User
from app.rbac import require_any_role

router = APIRouter()


class TemplateSummary(BaseModel):
    id: str
    name: str
    course_code: str | None
    semester: str | None
    instructor: str | None
    assignment_count: int

    model_config = {"from_attributes": True}


class TemplateCreate(BaseModel):
    name: str
    course_code: str | None = None
    semester: str | None = None
    instructor: str | None = None


class ImportResponse(BaseModel):
    course_id: str
    assignments_imported: int


def _template_summary(course: Course, db: Session) -> TemplateSummary:
    count = db.query(Assignment).filter(Assignment.course_id == course.id).count()
    return TemplateSummary(
        id=str(course.id),
        name=course.name,
        course_code=course.course_code,
        semester=course.semester,
        instructor=course.instructor,
        assignment_count=count,
    )


@router.get("", response_model=list[TemplateSummary])
def list_templates(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    templates = (
        db.query(Course)
        .filter(Course.is_template.is_(True))
        .order_by(Course.course_code.asc().nulls_last(), Course.name.asc())
        .all()
    )
    return [_template_summary(t, db) for t in templates]


@router.post("", response_model=TemplateSummary, status_code=status.HTTP_201_CREATED)
def publish_template(
    body: TemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_any_role("ta", "admin")),
):
    template = Course(
        user_id=None,
        is_template=True,
        published_by_user_id=current_user.id,
        **body.model_dump(),
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return _template_summary(template, db)


@router.post("/{template_id}/import", response_model=ImportResponse, status_code=status.HTTP_201_CREATED)
def import_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        tid = uuid.UUID(template_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Template not found")

    template = db.query(Course).filter(Course.id == tid, Course.is_template.is_(True)).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    new_course = Course(
        user_id=current_user.id,
        is_template=False,
        name=template.name,
        course_code=template.course_code,
        semester=template.semester,
        instructor=template.instructor,
        semester_start=template.semester_start,
        semester_end=template.semester_end,
    )
    db.add(new_course)
    db.flush()

    template_assignments = db.query(Assignment).filter(Assignment.course_id == tid).all()
    for ta in template_assignments:
        a = Assignment(
            course_id=new_course.id,
            title=ta.title,
            description=ta.description,
            due_date=ta.due_date,
            assignment_type=ta.assignment_type,
            weight=ta.weight,
            estimated_hours=ta.estimated_hours,
        )
        db.add(a)
        db.flush()
        _autogenerate_tasks(a, db)

    db.commit()
    return ImportResponse(
        course_id=str(new_course.id),
        assignments_imported=len(template_assignments),
    )
