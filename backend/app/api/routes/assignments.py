"""Assignment CRUD routes — scoped through the assignment's owning course."""

import math
import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.assignment import Assignment
from app.models.course import Course
from app.models.task import Task
from app.models.user import User

router = APIRouter()

ASSIGNMENT_TYPES = {"homework", "exam", "project", "reading", "quiz", "other"}
SUBTASK_SPLIT_THRESHOLD_HOURS = 4
SUBTASK_CHUNK_HOURS = 3


class AssignmentCreate(BaseModel):
    course_id: str
    title: str
    description: str | None = None
    due_date: datetime | None = None
    assignment_type: str = "homework"
    weight: float | None = None
    estimated_hours: int = 2


class AssignmentUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    due_date: datetime | None = None
    assignment_type: str | None = None
    weight: float | None = None
    estimated_hours: int | None = None


class AssignmentResponse(BaseModel):
    id: str
    course_id: str
    title: str
    description: str | None
    due_date: datetime | None
    assignment_type: str
    weight: float | None
    estimated_hours: int

    model_config = {"from_attributes": True}


def _to_response(a: Assignment) -> AssignmentResponse:
    return AssignmentResponse(
        id=str(a.id),
        course_id=str(a.course_id),
        title=a.title,
        description=a.description,
        due_date=a.due_date,
        assignment_type=a.assignment_type,
        weight=a.weight,
        estimated_hours=a.estimated_hours,
    )


def _owned_course(course_id: uuid.UUID, db: Session, user: User) -> Course:
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course or course.user_id != user.id:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


def _autogenerate_tasks(assignment: Assignment, db: Session) -> None:
    """Generate tasks for an assignment. Splits into subtasks when estimated_hours > threshold."""
    hours = max(1, assignment.estimated_hours)
    due = assignment.due_date

    if hours <= SUBTASK_SPLIT_THRESHOLD_HOURS:
        task = Task(
            assignment_id=assignment.id,
            title=f"Work on {assignment.title}",
            due_date=due,
            duration_minutes=hours * 60,
        )
        db.add(task)
        return

    num_chunks = math.ceil(hours / SUBTASK_CHUNK_HOURS)
    per_chunk_hours = math.ceil(hours / num_chunks)

    parent = Task(
        assignment_id=assignment.id,
        title=assignment.title,
        due_date=due,
        duration_minutes=hours * 60,
    )
    db.add(parent)
    db.flush()

    for i in range(num_chunks):
        chunk_due = None
        if due:
            offset_days = num_chunks - 1 - i
            chunk_due = due - timedelta(days=offset_days)
        db.add(
            Task(
                assignment_id=assignment.id,
                parent_task_id=parent.id,
                title=f"{assignment.title} — Part {i + 1}/{num_chunks}",
                due_date=chunk_due,
                duration_minutes=per_chunk_hours * 60,
            )
        )


@router.get("", response_model=list[AssignmentResponse])
def list_assignments(
    course_id: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = (
        db.query(Assignment)
        .join(Course, Assignment.course_id == Course.id)
        .filter(Course.user_id == current_user.id)
    )
    if course_id:
        try:
            q = q.filter(Assignment.course_id == uuid.UUID(course_id))
        except ValueError:
            return []
    q = q.order_by(Assignment.due_date.asc().nulls_last())
    return [_to_response(a) for a in q.all()]


@router.post("", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
def create_assignment(
    body: AssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if body.assignment_type not in ASSIGNMENT_TYPES:
        raise HTTPException(status_code=422, detail=f"Invalid assignment_type: {body.assignment_type}")
    try:
        cid = uuid.UUID(body.course_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Course not found")

    _owned_course(cid, db, current_user)

    assignment = Assignment(
        course_id=cid,
        title=body.title,
        description=body.description,
        due_date=body.due_date,
        assignment_type=body.assignment_type,
        weight=body.weight,
        estimated_hours=body.estimated_hours,
    )
    db.add(assignment)
    db.flush()
    _autogenerate_tasks(assignment, db)
    db.commit()
    db.refresh(assignment)
    return _to_response(assignment)


def _get_owned_assignment(assignment_id: str, db: Session, user: User) -> Assignment:
    try:
        aid = uuid.UUID(assignment_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Assignment not found")
    a = (
        db.query(Assignment)
        .join(Course, Assignment.course_id == Course.id)
        .filter(Assignment.id == aid, Course.user_id == user.id)
        .first()
    )
    if not a:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return a


@router.get("/{assignment_id}", response_model=AssignmentResponse)
def get_assignment(
    assignment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _to_response(_get_owned_assignment(assignment_id, db, current_user))


@router.patch("/{assignment_id}", response_model=AssignmentResponse)
def update_assignment(
    assignment_id: str,
    body: AssignmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    a = _get_owned_assignment(assignment_id, db, current_user)
    changes = body.model_dump(exclude_unset=True)
    if "assignment_type" in changes and changes["assignment_type"] not in ASSIGNMENT_TYPES:
        raise HTTPException(status_code=422, detail="Invalid assignment_type")
    for field, value in changes.items():
        setattr(a, field, value)
    db.commit()
    db.refresh(a)
    return _to_response(a)


@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_assignment(
    assignment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    a = _get_owned_assignment(assignment_id, db, current_user)
    db.delete(a)
    db.commit()
