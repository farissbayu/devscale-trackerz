"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-11-16
"""

from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

session_status = sa.Enum(
    "not_started",
    "in_progress",
    "completed",
    "skipped",
    name="sessionstatus",
)


def upgrade() -> None:
    op.create_table(
        "learning_phases",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("week_number", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_learning_phases_order_index", "learning_phases", ["order_index"])
    op.create_index("ix_learning_phases_week_number", "learning_phases", ["week_number"], unique=True)

    op.create_table(
        "learning_sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("phase_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("learning_objectives", sa.JSON(), nullable=False),
        sa.Column("topics", sa.JSON(), nullable=False),
        sa.Column("expected_deliverable", sa.String(), nullable=False),
        sa.Column("estimated_duration_minutes", sa.Integer(), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["phase_id"], ["learning_phases.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("phase_id", "order_index", name="uq_session_phase_order"),
    )
    op.create_index("ix_learning_sessions_phase_id", "learning_sessions", ["phase_id"])

    op.create_table(
        "session_progress",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("status", session_status, nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_duration_minutes", sa.Integer(), nullable=True),
        sa.Column("what_i_learned", sa.String(), nullable=False),
        sa.Column("what_i_understand", sa.String(), nullable=False),
        sa.Column("what_i_dont_understand", sa.String(), nullable=False),
        sa.Column("implementation_notes", sa.String(), nullable=False),
        sa.Column("reference_links", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["learning_sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("session_id"),
    )
    op.create_index("ix_session_progress_status", "session_progress", ["status"])

    op.create_table(
        "learning_activities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("activity_type", sa.String(length=50), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["learning_sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_learning_activities_session_id", "learning_activities", ["session_id"])
    op.create_index("ix_learning_activities_created_at", "learning_activities", ["created_at"])


def downgrade() -> None:
    op.drop_table("learning_activities")
    op.drop_table("session_progress")
    op.drop_table("learning_sessions")
    op.drop_table("learning_phases")
    session_status.drop(op.get_bind(), checkfirst=True)
