"""Pure progress rules. No database access so they are cheap to test."""

from collections.abc import Sequence

from app.models import SessionStatus
from app.schemas import PhaseStatus

FINAL_STATUSES = (SessionStatus.completed, SessionStatus.skipped)


def completion_percent(completed: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return round(completed / total * 100, 1)


def learning_hours(minutes: int) -> float:
    return round(minutes / 60, 1)


def derive_phase_status(statuses: Sequence[SessionStatus]) -> PhaseStatus:
    if statuses and all(status == SessionStatus.completed for status in statuses):
        return PhaseStatus.completed
    if any(status in (SessionStatus.completed, SessionStatus.in_progress) for status in statuses):
        return PhaseStatus.in_progress
    return PhaseStatus.not_started


def first_active_index(statuses: Sequence[SessionStatus]) -> int | None:
    """First session that is neither completed nor skipped, in curriculum order."""
    for index, status in enumerate(statuses):
        if status not in FINAL_STATUSES:
            return index
    return None


def is_curriculum_completed(statuses: Sequence[SessionStatus]) -> bool:
    return bool(statuses) and all(status == SessionStatus.completed for status in statuses)
