from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlalchemy import JSON, Column, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.types import TypeDecorator
from sqlmodel import Field, Relationship, SQLModel


class SessionStatus(str, Enum):
    not_started = "not_started"
    in_progress = "in_progress"
    completed = "completed"
    skipped = "skipped"


class UTCDateTime(TypeDecorator):
    """Persist naive UTC (SQLite has no timezone type) and read back aware UTC datetimes."""

    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(self, value: datetime | None, dialect):
        if value is None:
            return None
        if value.tzinfo is None:
            return value
        return value.astimezone(timezone.utc).replace(tzinfo=None)

    def process_result_value(self, value: datetime | None, dialect):
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class LearningPhase(SQLModel, table=True):
    __tablename__ = "learning_phases"

    id: int | None = Field(default=None, primary_key=True)
    week_number: int = Field(unique=True, index=True, ge=1)
    title: str = Field(max_length=200)
    description: str = Field(default="")
    order_index: int = Field(default=0, index=True)

    sessions: list["LearningSession"] = Relationship(back_populates="phase", cascade_delete=True)


class LearningSession(SQLModel, table=True):
    __tablename__ = "learning_sessions"
    __table_args__ = (UniqueConstraint("phase_id", "order_index", name="uq_session_phase_order"),)

    id: int | None = Field(default=None, primary_key=True)
    phase_id: int = Field(
        sa_column=Column(ForeignKey("learning_phases.id", ondelete="CASCADE"), nullable=False, index=True)
    )
    title: str = Field(max_length=300)
    description: str = Field(default="")
    learning_objectives: list[str] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    topics: list[str] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    expected_deliverable: str = Field(default="")
    source_url: str = Field(default="", max_length=1000)
    estimated_duration_minutes: int = Field(default=90, ge=1)
    order_index: int = Field(default=0)

    phase: LearningPhase | None = Relationship(back_populates="sessions")
    progress: Optional["SessionProgress"] = Relationship(
        back_populates="session", cascade_delete=True, sa_relationship_kwargs={"uselist": False}
    )


class SessionProgress(SQLModel, table=True):
    __tablename__ = "session_progress"

    id: int | None = Field(default=None, primary_key=True)
    session_id: int = Field(
        sa_column=Column(ForeignKey("learning_sessions.id", ondelete="CASCADE"), nullable=False, unique=True)
    )
    status: SessionStatus = Field(default=SessionStatus.not_started, index=True)
    started_at: datetime | None = Field(default=None, sa_column=Column(UTCDateTime(), nullable=True))
    completed_at: datetime | None = Field(default=None, sa_column=Column(UTCDateTime(), nullable=True))
    actual_duration_minutes: int | None = Field(default=None, ge=0)
    video_timestamp_seconds: int | None = Field(default=None, ge=0, le=86400)
    what_i_learned: str = Field(default="")
    what_i_understand: str = Field(default="")
    what_i_dont_understand: str = Field(default="")
    implementation_notes: str = Field(default="")
    created_at: datetime = Field(
        default_factory=utcnow, sa_column=Column(UTCDateTime(), nullable=False)
    )
    updated_at: datetime = Field(
        default_factory=utcnow, sa_column=Column(UTCDateTime(), nullable=False)
    )

    session: LearningSession | None = Relationship(back_populates="progress")


class LearningActivity(SQLModel, table=True):
    __tablename__ = "learning_activities"

    id: int | None = Field(default=None, primary_key=True)
    session_id: int = Field(
        sa_column=Column(ForeignKey("learning_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    )
    activity_type: str = Field(max_length=50)
    description: str = Field(default="")
    duration_minutes: int | None = Field(default=None, ge=0)
    created_at: datetime = Field(
        default_factory=utcnow, sa_column=Column(UTCDateTime(), nullable=False)
    )
