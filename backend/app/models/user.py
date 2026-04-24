import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(150), nullable=False)
    password_hash: Mapped[str | None] = mapped_column(String(255))
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    role = relationship("Role", back_populates="users")
    courses = relationship(
        "Course",
        back_populates="user",
        foreign_keys="Course.user_id",
        cascade="all, delete-orphan",
    )
    reminders = relationship("Reminder", back_populates="user", cascade="all, delete-orphan")
    study_sessions = relationship(
        "StudySession", back_populates="user", cascade="all, delete-orphan"
    )
    preference = relationship(
        "UserPreference", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User {self.email}>"
