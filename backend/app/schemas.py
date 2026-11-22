from datetime import datetime
from enum import Enum
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator

from app.models import SessionStatus


class PhaseStatus(str, Enum):
    not_started = "not_started"
    in_progress = "in_progress"
    completed = "completed"


class SessionRead(BaseModel):
    id: int
    phase_id: int
    title: str
    description: str
    learning_objectives: list[str]
    topics: list[str]
    expected_deliverable: str
    source_url: str
    estimated_duration_minutes: int
    order_index: int
    status: SessionStatus
    started_at: datetime | None
    completed_at: datetime | None
    actual_duration_minutes: int | None
    video_timestamp_seconds: int | None
    what_i_learned: str
    what_i_understand: str
    what_i_dont_understand: str
    implementation_notes: str


class SessionDetailRead(SessionRead):
    week_number: int
    phase_title: str
    next_session_id: int | None = None
    next_session_title: str | None = None


class PhaseRead(BaseModel):
    id: int
    week_number: int
    title: str
    description: str
    order_index: int
    status: PhaseStatus
    progress_percent: float
    completed_sessions: int
    total_sessions: int
    sessions: list[SessionRead]


class SessionBrief(BaseModel):
    id: int
    title: str
    week_number: int
    session_number: int
    status: SessionStatus
    estimated_duration_minutes: int
    learning_objectives: list[str]


class SessionSourcePayload(BaseModel):
    source_url: str = Field(default="", max_length=1000)

    @field_validator("source_url")
    @classmethod
    def validate_source_url(cls, value: str) -> str:
        value = value.strip()
        if not value:
            return ""
        parsed = urlparse(value)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise ValueError("Enter a valid http(s) URL")
        return value


class VideoTimestampPayload(BaseModel):
    seconds: int | None = Field(default=None, ge=0, le=86400)


class NotesPayload(BaseModel):
    what_i_learned: str | None = None
    what_i_understand: str | None = None
    what_i_dont_understand: str | None = None
    implementation_notes: str | None = None


class CompleteSessionRequest(NotesPayload):
    actual_duration_minutes: int = Field(ge=1, le=1440)


class OverallStats(BaseModel):
    completed_phases: int
    total_phases: int
    completed_sessions: int
    total_sessions: int
    progress_percent: float
    total_learning_minutes: int
    total_learning_hours: float


class SessionCounts(BaseModel):
    completed: int
    in_progress: int
    not_started: int
    skipped: int
    total: int


class CurrentPhaseRead(BaseModel):
    id: int
    week_number: int
    title: str
    status: PhaseStatus
    progress_percent: float
    completed_sessions: int
    total_sessions: int
    next_session: SessionBrief | None


class RecentActivityRead(BaseModel):
    session_id: int
    title: str
    week_number: int
    completed_at: datetime
    actual_duration_minutes: int | None


class DashboardRead(BaseModel):
    overall: OverallStats
    counts: SessionCounts
    current_phase: CurrentPhaseRead | None
    next_session: SessionBrief | None
    recent_activity: list[RecentActivityRead]
    curriculum_completed: bool


class HistoryItemRead(BaseModel):
    session_id: int
    title: str
    week_number: int
    phase_title: str
    status: SessionStatus
    activity_at: datetime | None
    completed_at: datetime | None
    actual_duration_minutes: int | None
    note_excerpt: str


class WeekProgressRead(BaseModel):
    week_number: int
    title: str
    status: PhaseStatus
    completed_sessions: int
    total_sessions: int
    progress_percent: float
    learning_minutes: int


class ProgressOverviewRead(BaseModel):
    progress_percent: float
    completed_sessions: int
    total_sessions: int
    total_learning_minutes: int
    total_learning_hours: float
    weeks: list[WeekProgressRead]
