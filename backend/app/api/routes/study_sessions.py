"""Study session routes — CRUD for personal study sessions."""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.study_session import StudySession
from app.models.user import User

router = APIRouter()


class StudySessionCreate(BaseModel):
    title: str
    description: str | None = None
    location: str | None = None
    starts_at: datetime
    ends_at: datetime


class StudySessionUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    location: str | None = None
    starts_at: datetime | None = None
    ends_at: datetime | None = None


class StudySessionResponse(BaseModel):
    id: str
    title: str
    description: str | None
    location: str | None
    starts_at: datetime
    ends_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


def _to_response(s: StudySession) -> StudySessionResponse:
    return StudySessionResponse(
        id=str(s.id),
        title=s.title,
        description=s.description,
        location=s.location,
        starts_at=s.starts_at,
        ends_at=s.ends_at,
        created_at=s.created_at,
    )


def _get_owned(session_id: str, db: Session, user: User) -> StudySession:
    try:
        sid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Study session not found")
    s = db.query(StudySession).filter(
        StudySession.id == sid, StudySession.user_id == user.id
    ).first()
    if not s:
        raise HTTPException(status_code=404, detail="Study session not found")
    return s


@router.get("", response_model=list[StudySessionResponse])
def list_study_sessions(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sessions = (
        db.query(StudySession)
        .filter(StudySession.user_id == current_user.id)
        .order_by(StudySession.starts_at.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [_to_response(s) for s in sessions]


@router.post("", response_model=StudySessionResponse, status_code=status.HTTP_201_CREATED)
def create_study_session(
    body: StudySessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if body.ends_at <= body.starts_at:
        raise HTTPException(status_code=422, detail="ends_at must be after starts_at")
    session = StudySession(user_id=current_user.id, **body.model_dump())
    db.add(session)
    db.commit()
    db.refresh(session)
    return _to_response(session)


@router.get("/{session_id}", response_model=StudySessionResponse)
def get_study_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _to_response(_get_owned(session_id, db, current_user))


@router.patch("/{session_id}", response_model=StudySessionResponse)
def update_study_session(
    session_id: str,
    body: StudySessionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    s = _get_owned(session_id, db, current_user)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(s, field, value)
    if s.ends_at <= s.starts_at:
        raise HTTPException(status_code=422, detail="ends_at must be after starts_at")
    db.commit()
    db.refresh(s)
    return _to_response(s)


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_study_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    s = _get_owned(session_id, db, current_user)
    db.delete(s)
    db.commit()
