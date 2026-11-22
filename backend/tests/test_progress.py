from app.models import SessionStatus
from app.schemas import PhaseStatus
from app.services.progress import (
    completion_percent,
    derive_phase_status,
    first_active_index,
    is_curriculum_completed,
    learning_hours,
)

ALL_DONE = [SessionStatus.completed, SessionStatus.completed]


def test_completion_percent_rounds_and_handles_empty() -> None:
    assert completion_percent(0, 0) == 0.0
    assert completion_percent(1, 4) == 25.0
    assert completion_percent(1, 64) == 1.6
    assert completion_percent(3, 3) == 100.0


def test_learning_hours() -> None:
    assert learning_hours(0) == 0.0
    assert learning_hours(75) == 1.2
    assert learning_hours(600) == 10.0


def test_phase_status() -> None:
    assert derive_phase_status([]) == PhaseStatus.not_started
    assert derive_phase_status([SessionStatus.not_started] * 4) == PhaseStatus.not_started
    assert derive_phase_status([SessionStatus.in_progress, SessionStatus.not_started]) == PhaseStatus.in_progress
    assert derive_phase_status(ALL_DONE) == PhaseStatus.completed
    # Skipped sessions never count as completed.
    assert (
        derive_phase_status([SessionStatus.completed, SessionStatus.skipped])
        == PhaseStatus.in_progress
    )


def test_first_active_skips_completed_and_skipped() -> None:
    statuses = [
        SessionStatus.completed,
        SessionStatus.skipped,
        SessionStatus.in_progress,
        SessionStatus.not_started,
    ]
    assert first_active_index(statuses) == 2
    assert first_active_index([SessionStatus.completed, SessionStatus.skipped]) is None
    assert first_active_index([]) is None


def test_curriculum_completed_requires_every_session_completed() -> None:
    assert is_curriculum_completed(ALL_DONE)
    assert not is_curriculum_completed(
        [SessionStatus.completed, SessionStatus.skipped]
    )
    assert not is_curriculum_completed([])
