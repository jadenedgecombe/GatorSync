"""Schedule + workload views.

- GET /schedule/week?start=YYYY-MM-DD — 7-day schedule of scheduled tasks.
- GET /schedule/day?date=YYYY-MM-DD — single-day schedule.
- GET /schedule/heatmap?start=YYYY-MM-DD&days=7 — workload per day (green/yellow/red).
- GET /schedule/overload?date=YYYY-MM-DD — bool + minutes for overload warning.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, time, timedelta, timezone
from typing import Iterable
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.assignment import Assignment
from app.models.course import Course
from app.models.task import Task
from app.models.user import User

router = APIRouter()

HEATMAP_YELLOW_MINUTES = 180  # 3 hours
HEATMAP_RED_MINUTES = 360  # 6 hours
OVERLOAD_MINUTES = HEATMAP_RED_MINUTES

# All day-bucketing uses this timezone so "today" matches the user's wall clock,
# not the UTC day. UF is in America/New_York; fetching the user's own tz is a
# future improvement, but this covers the current student cohort correctly.
LOCAL_TZ = ZoneInfo("America/New_York")


class ScheduledTask(BaseModel):
    id: str
    title: str
    course_code: str | None
    scheduled_start: datetime | None
    scheduled_end: datetime | None
    due_date: datetime | None
    duration_minutes: int
    is_completed: bool


class DaySchedule(BaseModel):
    date: date
    tasks: list[ScheduledTask]
    total_minutes: int


class WeekSchedule(BaseModel):
    start: date
    days: list[DaySchedule]


class HeatmapCell(BaseModel):
    date: date
    minutes: int
    bucket: str  # "empty" | "light" | "medium" | "heavy"


class HeatmapResponse(BaseModel):
    start: date
    days: list[HeatmapCell]


class OverloadResponse(BaseModel):
    date: date
    minutes: int
    is_overloaded: bool
    threshold_minutes: int


def _bucket(minutes: int) -> str:
    if minutes == 0:
        return "empty"
    if minutes < HEATMAP_YELLOW_MINUTES:
        return "light"
    if minutes < HEATMAP_RED_MINUTES:
        return "medium"
    return "heavy"


def _day_bounds(d: date) -> tuple[datetime, datetime]:
    """Return UTC-aware datetimes covering the local-time day `d`.

    e.g. April 24 in ET becomes 04:00 UTC Apr 24 → 04:00 UTC Apr 25, so a task
    stored in UTC that falls on Apr 24 wall-clock shows up in the right bucket.
    """
    start_local = datetime.combine(d, time.min, tzinfo=LOCAL_TZ)
    end_local = datetime.combine(d, time.max, tzinfo=LOCAL_TZ)
    return start_local.astimezone(timezone.utc), end_local.astimezone(timezone.utc)


def _anchor_date_local(task: Task) -> date | None:
    """Which local-timezone day does this task belong to?"""
    dt = task.scheduled_start or task.due_date
    if not dt:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(LOCAL_TZ).date()


def _local_today() -> date:
    return datetime.now(LOCAL_TZ).date()


def _fetch_tasks_between(
    user: User, start: datetime, end: datetime, db: Session
) -> list[tuple[Task, Assignment, Course]]:
    rows = (
        db.query(Task, Assignment, Course)
        .join(Assignment, Task.assignment_id == Assignment.id)
        .join(Course, Assignment.course_id == Course.id)
        .filter(Course.user_id == user.id)
        .filter(
            (
                (Task.scheduled_start.isnot(None))
                & (Task.scheduled_start >= start)
                & (Task.scheduled_start <= end)
            )
            | (
                (Task.scheduled_start.is_(None))
                & (Task.due_date.isnot(None))
                & (Task.due_date >= start)
                & (Task.due_date <= end)
            )
        )
        .all()
    )
    return rows


def _serialize(rows: Iterable[tuple[Task, Assignment, Course]]) -> list[ScheduledTask]:
    out: list[ScheduledTask] = []
    for t, _a, c in rows:
        out.append(
            ScheduledTask(
                id=str(t.id),
                title=t.title,
                course_code=c.course_code,
                scheduled_start=t.scheduled_start,
                scheduled_end=t.scheduled_end,
                due_date=t.due_date,
                duration_minutes=t.duration_minutes,
                is_completed=t.is_completed,
            )
        )
    return out


@router.get("/week", response_model=WeekSchedule)
def week_schedule(
    start: date | None = Query(None, description="Start date of the week (defaults to today)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    start_date = start or _local_today()
    end_date = start_date + timedelta(days=6)
    range_start, _ = _day_bounds(start_date)
    _, range_end = _day_bounds(end_date)

    rows = _fetch_tasks_between(current_user, range_start, range_end, db)

    by_day: dict[date, list[tuple[Task, Assignment, Course]]] = defaultdict(list)
    for t, a, c in rows:
        d = _anchor_date_local(t)
        if d and start_date <= d <= end_date:
            by_day[d].append((t, a, c))

    days: list[DaySchedule] = []
    for i in range(7):
        d = start_date + timedelta(days=i)
        day_rows = by_day.get(d, [])
        days.append(
            DaySchedule(
                date=d,
                tasks=_serialize(day_rows),
                total_minutes=sum(t.duration_minutes for (t, _a, _c) in day_rows),
            )
        )
    return WeekSchedule(start=start_date, days=days)


@router.get("/day", response_model=DaySchedule)
def day_schedule(
    date_: date | None = Query(None, alias="date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    day = date_ or _local_today()
    start, end = _day_bounds(day)
    rows = _fetch_tasks_between(current_user, start, end, db)
    return DaySchedule(
        date=day,
        tasks=_serialize(rows),
        total_minutes=sum(t.duration_minutes for (t, _a, _c) in rows),
    )


@router.get("/heatmap", response_model=HeatmapResponse)
def heatmap(
    start: date | None = Query(None),
    days: int = Query(7, ge=1, le=31),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    start_date = start or _local_today()
    end_date = start_date + timedelta(days=days - 1)
    range_start, _ = _day_bounds(start_date)
    _, range_end = _day_bounds(end_date)

    rows = _fetch_tasks_between(current_user, range_start, range_end, db)
    totals: dict[date, int] = defaultdict(int)
    for t, _a, _c in rows:
        d = _anchor_date_local(t)
        if d and start_date <= d <= end_date:
            totals[d] += t.duration_minutes

    cells = []
    for i in range(days):
        d = start_date + timedelta(days=i)
        minutes = totals.get(d, 0)
        cells.append(HeatmapCell(date=d, minutes=minutes, bucket=_bucket(minutes)))
    return HeatmapResponse(start=start_date, days=cells)


@router.get("/overload", response_model=OverloadResponse)
def overload(
    date_: date | None = Query(None, alias="date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    day = date_ or _local_today()
    start, end = _day_bounds(day)
    rows = _fetch_tasks_between(current_user, start, end, db)
    minutes = sum(t.duration_minutes for (t, _a, _c) in rows)
    return OverloadResponse(
        date=day,
        minutes=minutes,
        is_overloaded=minutes >= OVERLOAD_MINUTES,
        threshold_minutes=OVERLOAD_MINUTES,
    )
