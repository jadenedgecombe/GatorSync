"""sprint 2 schema expansion

Adds Assignment.assignment_type, weight, estimated_hours.
Adds Course.semester_start, semester_end, is_template, published_by_user_id.
Makes Course.user_id nullable so templates can exist without an owning student.
Adds Task.parent_task_id, scheduled_start, scheduled_end, duration_minutes.

Revision ID: 7a1b2c3d4e5f
Revises: 3f2aea097707
Create Date: 2026-04-24
"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "7a1b2c3d4e5f"
down_revision: Union[str, None] = "3f2aea097707"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Assignment expansions
    op.add_column(
        "assignments",
        sa.Column("assignment_type", sa.String(30), nullable=False, server_default="homework"),
    )
    op.add_column("assignments", sa.Column("weight", sa.Float, nullable=True))
    op.add_column(
        "assignments",
        sa.Column("estimated_hours", sa.Integer, nullable=False, server_default="2"),
    )

    # Course expansions — make user_id nullable for templates
    op.alter_column("courses", "user_id", nullable=True)
    op.add_column("courses", sa.Column("semester_start", sa.Date, nullable=True))
    op.add_column("courses", sa.Column("semester_end", sa.Date, nullable=True))
    op.add_column(
        "courses",
        sa.Column("is_template", sa.Boolean, nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "courses",
        sa.Column(
            "published_by_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=True,
        ),
    )

    # Task scheduling + subtask support
    op.add_column(
        "tasks",
        sa.Column(
            "parent_task_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tasks.id"),
            nullable=True,
        ),
    )
    op.add_column("tasks", sa.Column("scheduled_start", sa.DateTime(timezone=True), nullable=True))
    op.add_column("tasks", sa.Column("scheduled_end", sa.DateTime(timezone=True), nullable=True))
    op.add_column(
        "tasks",
        sa.Column("duration_minutes", sa.Integer, nullable=False, server_default="60"),
    )


def downgrade() -> None:
    op.drop_column("tasks", "duration_minutes")
    op.drop_column("tasks", "scheduled_end")
    op.drop_column("tasks", "scheduled_start")
    op.drop_column("tasks", "parent_task_id")

    op.drop_column("courses", "published_by_user_id")
    op.drop_column("courses", "is_template")
    op.drop_column("courses", "semester_end")
    op.drop_column("courses", "semester_start")
    op.alter_column("courses", "user_id", nullable=False)

    op.drop_column("assignments", "estimated_hours")
    op.drop_column("assignments", "weight")
    op.drop_column("assignments", "assignment_type")
