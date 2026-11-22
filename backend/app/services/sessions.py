from fastapi import HTTPException
from sqlmodel import Session, select

from app.models import (
    LearningActivity,
    LearningSession,
    SessionProgress,
    SessionStatus,
    utcnow,
)
from app.schemas import (
    CompleteSessionRequest,
    NotesPayload,
    SessionDetailRead,
    SessionSourcePayload,
    VideoTimestampPayload,
)
from app.services.curriculum import get_session_detail, load_session

NOTE_FIELDS = (
    "what_i_learned",
    "what_i_understand",
    "what_i_dont_understand",
    "implementation_notes",
)


def _progress_for(db: Session, session: LearningSession) -> SessionProgress:
    progress = db.exec(select(SessionProgress).where(SessionProgress.session_id == session.id)).first()
    if progress is None:
        raise HTTPException(status_code=500, detail="Session progress record is missing")
    return progress


def _apply_notes(progress: SessionProgress, payload: NotesPayload) -> None:
    for field in NOTE_FIELDS:
        value = getattr(payload, field)
        if value is not None:
            setattr(progress, field, value)


def _log(db: Session, session_id: int, activity_type: str, description: str, duration: int | None = None) -> None:
    db.add(
        LearningActivity(
            session_id=session_id,
            activity_type=activity_type,
            description=description,
            duration_minutes=duration,
        )
    )


def _commit(db: Session, session_id: int) -> SessionDetailRead:
    db.commit()
    return get_session_detail(db, session_id)


def start_session(db: Session, session_id: int) -> SessionDetailRead:
    session = load_session(db, session_id)
    progress = _progress_for(db, session)
    if progress.status == SessionStatus.completed:
        raise HTTPException(status_code=409, detail="Session is already completed. Reset it to start again.")
    progress.status = SessionStatus.in_progress
    if progress.started_at is None:
        progress.started_at = utcnow()
    progress.updated_at = utcnow()
    _log(db, session_id, "started", f"Started session: {session.title}")
    return _commit(db, session_id)


def complete_session(db: Session, session_id: int, payload: CompleteSessionRequest) -> SessionDetailRead:
    session = load_session(db, session_id)
    progress = _progress_for(db, session)
    if progress.status == SessionStatus.completed:
        raise HTTPException(status_code=409, detail="Session is already completed.")
    now = utcnow()
    if progress.started_at is None:
        progress.started_at = now
    progress.status = SessionStatus.completed
    progress.completed_at = now
    progress.actual_duration_minutes = payload.actual_duration_minutes
    progress.updated_at = now
    _apply_notes(progress, payload)
    _log(
        db,
        session_id,
        "completed",
        f"Completed session: {session.title}",
        payload.actual_duration_minutes,
    )
    return _commit(db, session_id)


def save_source(db: Session, session_id: int, payload: SessionSourcePayload) -> SessionDetailRead:
    session = load_session(db, session_id)
    session.source_url = payload.source_url
    db.add(session)
    db.commit()
    return get_session_detail(db, session_id)


def save_timestamp(
    db: Session, session_id: int, payload: VideoTimestampPayload
) -> SessionDetailRead:
    session = load_session(db, session_id)
    progress = _progress_for(db, session)
    progress.video_timestamp_seconds = payload.seconds
    progress.updated_at = utcnow()
    db.commit()
    return get_session_detail(db, session_id)


def save_notes(db: Session, session_id: int, payload: NotesPayload) -> SessionDetailRead:
    session = load_session(db, session_id)
    progress = _progress_for(db, session)
    _apply_notes(progress, payload)
    progress.updated_at = utcnow()
    return _commit(db, session_id)


def skip_session(db: Session, session_id: int) -> SessionDetailRead:
    session = load_session(db, session_id)
    progress = _progress_for(db, session)
    if progress.status == SessionStatus.completed:
        raise HTTPException(status_code=409, detail="Completed sessions cannot be skipped. Reset it first.")
    progress.status = SessionStatus.skipped
    progress.completed_at = None
    progress.actual_duration_minutes = None
    progress.updated_at = utcnow()
    _log(db, session_id, "skipped", f"Skipped session: {session.title}")
    return _commit(db, session_id)


def reset_session(db: Session, session_id: int) -> SessionDetailRead:
    session = load_session(db, session_id)
    progress = _progress_for(db, session)
    progress.status = SessionStatus.not_started
    progress.started_at = None
    progress.completed_at = None
    progress.actual_duration_minutes = None
    progress.updated_at = utcnow()
    _log(db, session_id, "reset", f"Reset session: {session.title}")
    return _commit(db, session_id)
