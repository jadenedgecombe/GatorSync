"""Task routes — list, toggle, reschedule (drag-and-drop)."""

import uuid
from datetime import datetime

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


class TaskUpdate(BaseModel):
    title: str | None = None
    is_completed: bool | None = None
    scheduled_start: datetime | None = None
    scheduled_end: datetime | None = None
    duration_minutes: int | None = None


class TaskResponse(BaseModel):
    id: str
    assignment_id: str
    parent_task_id: str | None
    course_id: str
    course_code: str | None
    title: str
    is_completed: bool
    due_date: datetime | None
    scheduled_start: datetime | None
    scheduled_end: datetime | None
    duration_minutes: int

    model_config = {"from_attributes": True}


def _to_response(t: Task, a: Assignment, c: Course) -> TaskResponse:
    return TaskResponse(
        id=str(t.id),
        assignment_id=str(t.assignment_id),
        parent_task_id=str(t.parent_task_id) if t.parent_task_id else None,
        course_id=str(c.id),
        course_code=c.course_code,
        title=t.title,
        is_completed=t.is_completed,
        due_date=t.due_date,
        scheduled_start=t.scheduled_start,
        scheduled_end=t.scheduled_end,
        duration_minutes=t.duration_minutes,
    )


@router.get("", response_model=list[TaskResponse])
def list_tasks(
    include_completed: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = (
        db.query(Task, Assignment, Course)
        .join(Assignment, Task.assignment_id == Assignment.id)
        .join(Course, Assignment.course_id == Course.id)
        .filter(Course.user_id == current_user.id)
    )
    if not include_completed:
        q = q.filter(Task.is_completed.is_(False))
    rows = q.order_by(Task.due_date.asc().nulls_last()).all()
    return [_to_response(t, a, c) for (t, a, c) in rows]


def _owned_task(task_id: str, db: Session, user: User):
    try:
        tid = uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Task not found")
    row = (
        db.query(Task, Assignment, Course)
        .join(Assignment, Task.assignment_id == Assignment.id)
        .join(Course, Assignment.course_id == Course.id)
        .filter(Task.id == tid, Course.user_id == user.id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Task not found")
    return row


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: str,
    body: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    t, a, c = _owned_task(task_id, db, current_user)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(t, field, value)
    db.commit()
    db.refresh(t)
    return _to_response(t, a, c)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    t, _, _ = _owned_task(task_id, db, current_user)
    db.delete(t)
    db.commit()
