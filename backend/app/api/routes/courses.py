"""Course CRUD routes — scoped to the authenticated user."""

import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.course import Course
from app.models.user import User

router = APIRouter()


class CourseCreate(BaseModel):
    name: str
    course_code: str | None = None
    semester: str | None = None
    instructor: str | None = None
    semester_start: date | None = None
    semester_end: date | None = None


class CourseUpdate(BaseModel):
    name: str | None = None
    course_code: str | None = None
    semester: str | None = None
    instructor: str | None = None
    semester_start: date | None = None
    semester_end: date | None = None


class CourseResponse(BaseModel):
    id: str
    name: str
    course_code: str | None
    semester: str | None
    instructor: str | None
    semester_start: date | None
    semester_end: date | None
    is_template: bool

    model_config = {"from_attributes": True}


def _to_response(c: Course) -> CourseResponse:
    return CourseResponse(
        id=str(c.id),
        name=c.name,
        course_code=c.course_code,
        semester=c.semester,
        instructor=c.instructor,
        semester_start=c.semester_start,
        semester_end=c.semester_end,
        is_template=c.is_template,
    )


@router.get("", response_model=list[CourseResponse])
def list_courses(
    search: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Course).filter(
        Course.user_id == current_user.id, Course.is_template.is_(False)
    )
    if search:
        term = f"%{search}%"
        q = q.filter(
            Course.name.ilike(term) | Course.course_code.ilike(term) | Course.instructor.ilike(term)
        )
    courses = q.order_by(Course.created_at.desc()).offset(skip).limit(limit).all()
    return [_to_response(c) for c in courses]


@router.post("", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(
    body: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    course = Course(user_id=current_user.id, is_template=False, **body.model_dump())
    db.add(course)
    db.commit()
    db.refresh(course)
    return _to_response(course)


def _get_owned_course(course_id: str, db: Session, user: User) -> Course:
    try:
        cid = uuid.UUID(course_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Course not found")
    course = db.query(Course).filter(Course.id == cid).first()
    if not course or course.user_id != user.id:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.get("/{course_id}", response_model=CourseResponse)
def get_course(
    course_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _to_response(_get_owned_course(course_id, db, current_user))


@router.patch("/{course_id}", response_model=CourseResponse)
def update_course(
    course_id: str,
    body: CourseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    course = _get_owned_course(course_id, db, current_user)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(course, field, value)
    db.commit()
    db.refresh(course)
    return _to_response(course)


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
    course_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    course = _get_owned_course(course_id, db, current_user)
    db.delete(course)
    db.commit()
