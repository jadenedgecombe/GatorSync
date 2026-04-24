"""Reminder routes + auto-sync from tasks with upcoming due dates."""

import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.assignment import Assignment
from app.models.course import Course
from app.models.reminder import Reminder
from app.models.task import Task
from app.models.user import User

router = APIRouter()

REMINDER_LEAD_HOURS = 24


class ReminderResponse(BaseModel):
    id: str
    title: str
    message: str | None
    remind_at: datetime
    is_dismissed: bool

    model_config = {"from_attributes": True}


class ReminderCreate(BaseModel):
    title: str
    message: str | None = None
    remind_at: datetime


def _to_response(r: Reminder) -> ReminderResponse:
    return ReminderResponse(
        id=str(r.id),
        title=r.title,
        message=r.message,
        remind_at=r.remind_at,
        is_dismissed=r.is_dismissed,
    )


def _sync_from_tasks(user: User, db: Session) -> int:
    """Create Reminder rows for any incomplete tasks whose due_date is within the lead window.

    Idempotent: skips tasks that already have a matching reminder.
    Returns number of newly created reminders.
    """
    now = datetime.now(timezone.utc)
    window_end = now + timedelta(hours=REMINDER_LEAD_HOURS)

    existing_titles = {
        r.title
        for r in db.query(Reminder).filter(
            Reminder.user_id == user.id, Reminder.is_dismissed.is_(False)
        )
    }

    rows = (
        db.query(Task, Assignment, Course)
        .join(Assignment, Task.assignment_id == Assignment.id)
        .join(Course, Assignment.course_id == Course.id)
        .filter(
            Course.user_id == user.id,
            Task.is_completed.is_(False),
            Task.due_date.isnot(None),
            Task.due_date <= window_end,
            Task.due_date >= now - timedelta(hours=1),
        )
        .all()
    )

    created = 0
    for task, assignment, course in rows:
        label = f"{course.course_code or course.name}: {task.title}"
        if label in existing_titles:
            continue
        db.add(
            Reminder(
                user_id=user.id,
                title=label,
                message=f"Due {task.due_date.strftime('%a %b %d, %I:%M %p')}",
                remind_at=max(task.due_date - timedelta(hours=REMINDER_LEAD_HOURS), now),
            )
        )
        created += 1

    if created:
        db.commit()
    return created


@router.get("", response_model=list[ReminderResponse])
def list_reminders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _sync_from_tasks(current_user, db)
    reminders = (
        db.query(Reminder)
        .filter(Reminder.user_id == current_user.id, Reminder.is_dismissed.is_(False))
        .order_by(Reminder.remind_at.asc())
        .all()
    )
    return [_to_response(r) for r in reminders]


@router.post("", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED)
def create_reminder(
    body: ReminderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    r = Reminder(user_id=current_user.id, **body.model_dump())
    db.add(r)
    db.commit()
    db.refresh(r)
    return _to_response(r)


@router.post("/{reminder_id}/dismiss", response_model=ReminderResponse)
def dismiss_reminder(
    reminder_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        rid = uuid.UUID(reminder_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Reminder not found")
    r = db.query(Reminder).filter(Reminder.id == rid, Reminder.user_id == current_user.id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Reminder not found")
    r.is_dismissed = True
    db.commit()
    db.refresh(r)
    return _to_response(r)
