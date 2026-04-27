"""User preferences routes — GET and PATCH /preferences."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.user import User
from app.models.user_preference import UserPreference

router = APIRouter()

VALID_TIMEZONES = [
    "America/New_York",
    "America/Chicago",
    "America/Denver",
    "America/Los_Angeles",
    "America/Phoenix",
    "America/Anchorage",
    "Pacific/Honolulu",
    "UTC",
]


class PreferenceUpdate(BaseModel):
    dark_mode: bool | None = None
    timezone: str | None = None
    notification_email: bool | None = None
    notification_push: bool | None = None


class PreferenceResponse(BaseModel):
    dark_mode: bool
    timezone: str
    notification_email: bool
    notification_push: bool

    model_config = {"from_attributes": True}


def _get_or_create_prefs(user: User, db: Session) -> UserPreference:
    pref = db.query(UserPreference).filter(UserPreference.user_id == user.id).first()
    if not pref:
        pref = UserPreference(user_id=user.id)
        db.add(pref)
        db.commit()
        db.refresh(pref)
    return pref


@router.get("", response_model=PreferenceResponse)
def get_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pref = _get_or_create_prefs(current_user, db)
    return PreferenceResponse(
        dark_mode=pref.dark_mode,
        timezone=pref.timezone,
        notification_email=pref.notification_email,
        notification_push=pref.notification_push,
    )


@router.patch("", response_model=PreferenceResponse)
def update_preferences(
    body: PreferenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pref = _get_or_create_prefs(current_user, db)
    changes = body.model_dump(exclude_unset=True)
    if "timezone" in changes and changes["timezone"] not in VALID_TIMEZONES:
        changes["timezone"] = "America/New_York"
    for field, value in changes.items():
        setattr(pref, field, value)
    db.commit()
    db.refresh(pref)
    return PreferenceResponse(
        dark_mode=pref.dark_mode,
        timezone=pref.timezone,
        notification_email=pref.notification_email,
        notification_push=pref.notification_push,
    )
