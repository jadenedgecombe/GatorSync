import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    course_code: Mapped[str | None] = mapped_column(String(20))
    semester: Mapped[str | None] = mapped_column(String(20))
    instructor: Mapped[str | None] = mapped_column(String(150))
    semester_start: Mapped[date | None] = mapped_column(Date)
    semester_end: Mapped[date | None] = mapped_column(Date)
    is_template: Mapped[bool] = mapped_column(Boolean, default=False)
    published_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    user = relationship("User", back_populates="courses", foreign_keys=[user_id])
    assignments = relationship(
        "Assignment", back_populates="course", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Course {self.course_code} — {self.name}>"
