from datetime import date, datetime, timezone

from fastapi import HTTPException
from sqlmodel import Session, select
from sqlalchemy import and_, or_
from sqlalchemy.orm import selectinload

from app.config import get_settings
from app.models import LearningPhase, LearningSession, SessionProgress, SessionStatus
from app.schemas import (
    CurrentPhaseRead,
    DashboardRead,
    HistoryItemRead,
    OverallStats,
    PhaseRead,
    PhaseStatus,
    ProgressOverviewRead,
    RecentActivityRead,
    SessionBrief,
    SessionCounts,
    SessionDetailRead,
    SessionRead,
    WeekProgressRead,
)
from app.services.progress import (
    completion_percent,
    derive_phase_status,
    first_active_index,
    is_curriculum_completed,
    learning_hours,
)


def load_phases(db: Session) -> list[LearningPhase]:
    statement = (
        select(LearningPhase)
        .options(selectinload(LearningPhase.sessions).selectinload(LearningSession.progress))
        .order_by(LearningPhase.order_index)
    )
    phases = list(db.exec(statement).all())
    for phase in phases:
        phase.sessions.sort(key=lambda session: session.order_index)
    return phases


def load_session(db: Session, session_id: int) -> LearningSession:
    statement = (
        select(LearningSession)
        .where(LearningSession.id == session_id)
        .options(selectinload(LearningSession.phase), selectinload(LearningSession.progress))
    )
    session = db.exec(statement).first()
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


def session_status(session: LearningSession) -> SessionStatus:
    return session.progress.status if session.progress else SessionStatus.not_started


def session_read(session: LearningSession) -> SessionRead:
    progress = session.progress
    return SessionRead(
        id=session.id,
        phase_id=session.phase_id,
        title=session.title,
        description=session.description,
        learning_objectives=session.learning_objectives,
        topics=session.topics,
        expected_deliverable=session.expected_deliverable,
        source_url=session.source_url,
        estimated_duration_minutes=session.estimated_duration_minutes,
        order_index=session.order_index,
        status=progress.status if progress else SessionStatus.not_started,
        started_at=progress.started_at if progress else None,
        completed_at=progress.completed_at if progress else None,
        actual_duration_minutes=progress.actual_duration_minutes if progress else None,
        video_timestamp_seconds=progress.video_timestamp_seconds if progress else None,
        what_i_learned=progress.what_i_learned if progress else "",
        what_i_understand=progress.what_i_understand if progress else "",
        what_i_dont_understand=progress.what_i_dont_understand if progress else "",
        implementation_notes=progress.implementation_notes if progress else "",
    )


def session_detail_read(session: LearningSession) -> SessionDetailRead:
    base = session_read(session).model_dump()
    return SessionDetailRead(
        **base,
        week_number=session.phase.week_number if session.phase else 0,
        phase_title=session.phase.title if session.phase else "",
    )


def phase_read(phase: LearningPhase) -> PhaseRead:
    statuses = [session_status(session) for session in phase.sessions]
    completed = sum(status == SessionStatus.completed for status in statuses)
    return PhaseRead(
        id=phase.id,
        week_number=phase.week_number,
        title=phase.title,
        description=phase.description,
        order_index=phase.order_index,
        status=derive_phase_status(statuses),
        progress_percent=completion_percent(completed, len(statuses)),
        completed_sessions=completed,
        total_sessions=len(statuses),
        sessions=[session_read(session) for session in phase.sessions],
    )


def get_session_detail(db: Session, session_id: int) -> SessionDetailRead:
    session = load_session(db, session_id)
    detail = session_detail_read(session)
    if session.phase is None:
        return detail
    next_session = db.exec(
        select(LearningSession)
        .join(LearningPhase, LearningSession.phase_id == LearningPhase.id)
        .where(
            or_(
                LearningPhase.order_index > session.phase.order_index,
                and_(
                    LearningPhase.order_index == session.phase.order_index,
                    LearningSession.order_index > session.order_index,
                ),
            )
        )
        .order_by(LearningPhase.order_index, LearningSession.order_index)
        .limit(1)
    ).first()
    if next_session is None:
        return detail
    return detail.model_copy(
        update={
            "next_session_id": next_session.id,
            "next_session_title": next_session.title,
        }
    )


def get_phase(db: Session, phase_id: int) -> PhaseRead:
    statement = (
        select(LearningPhase)
        .where(LearningPhase.id == phase_id)
        .options(selectinload(LearningPhase.sessions).selectinload(LearningSession.progress))
    )
    phase = db.exec(statement).first()
    if phase is None:
        raise HTTPException(status_code=404, detail="Phase not found")
    phase.sessions.sort(key=lambda session: session.order_index)
    return phase_read(phase)


def ordered_sessions(phases: list[LearningPhase]) -> list[LearningSession]:
    return [session for phase in phases for session in phase.sessions]


def _brief(session: LearningSession, week_number: int) -> SessionBrief:
    return SessionBrief(
        id=session.id,
        title=session.title,
        week_number=week_number,
        session_number=session.order_index,
        status=session_status(session),
        estimated_duration_minutes=session.estimated_duration_minutes,
        learning_objectives=session.learning_objectives,
    )


def get_dashboard(db: Session) -> DashboardRead:
    phases = load_phases(db)
    sessions = ordered_sessions(phases)
    statuses = [session_status(session) for session in sessions]

    completed_sessions = sum(status == SessionStatus.completed for status in statuses)
    total_learning_minutes = sum(
        session.progress.actual_duration_minutes or 0
        for session in sessions
        if session.progress and session.progress.status == SessionStatus.completed
    )
    completed_phases = sum(
        derive_phase_status([session_status(session) for session in phase.sessions]) == PhaseStatus.completed
        for phase in phases
    )

    next_index = first_active_index(statuses)
    next_session = None
    current_phase = None
    if next_index is not None:
        next_model = sessions[next_index]
        next_session = _brief(next_model, next_model.phase.week_number)
        phase = next_model.phase
        phase_statuses = [session_status(session) for session in phase.sessions]
        phase_completed = sum(status == SessionStatus.completed for status in phase_statuses)
        current_phase = CurrentPhaseRead(
            id=phase.id,
            week_number=phase.week_number,
            title=phase.title,
            status=derive_phase_status(phase_statuses),
            progress_percent=completion_percent(phase_completed, len(phase_statuses)),
            completed_sessions=phase_completed,
            total_sessions=len(phase_statuses),
            next_session=next_session,
        )

    recent = sorted(
        (
            session
            for session in sessions
            if session.progress
            and session.progress.status == SessionStatus.completed
            and session.progress.completed_at is not None
        ),
        key=lambda session: session.progress.completed_at,
        reverse=True,
    )[:5]

    return DashboardRead(
        overall=OverallStats(
            completed_phases=completed_phases,
            total_phases=len(phases),
            completed_sessions=completed_sessions,
            total_sessions=len(sessions),
            progress_percent=completion_percent(completed_sessions, len(sessions)),
            total_learning_minutes=total_learning_minutes,
            total_learning_hours=learning_hours(total_learning_minutes),
        ),
        counts=SessionCounts(
            completed=completed_sessions,
            in_progress=statuses.count(SessionStatus.in_progress),
            not_started=statuses.count(SessionStatus.not_started),
            skipped=statuses.count(SessionStatus.skipped),
            total=len(sessions),
        ),
        current_phase=current_phase,
        next_session=next_session,
        recent_activity=[
            RecentActivityRead(
                session_id=session.id,
                title=session.title,
                week_number=session.phase.week_number,
                completed_at=session.progress.completed_at,
                actual_duration_minutes=session.progress.actual_duration_minutes,
            )
            for session in recent
        ],
        curriculum_completed=is_curriculum_completed(statuses),
    )


def _activity_at(session: LearningSession):
    if session.progress is None:
        return None
    return session.progress.completed_at or session.progress.started_at


def _local_date(value: datetime) -> date:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(get_settings().tzinfo).date()


def _note_excerpt(session: LearningSession) -> str:
    if session.progress is None:
        return ""
    for value in (
        session.progress.what_i_learned,
        session.progress.implementation_notes,
        session.progress.what_i_dont_understand,
    ):
        if value.strip():
            return value.strip()[:140]
    return ""


def get_history(
    db: Session,
    *,
    week: int | None = None,
    phase_id: int | None = None,
    status: SessionStatus | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> list[HistoryItemRead]:
    # ponytail: 80 sessions fit in memory; push these filters into SQL if the curriculum grows.
    phases = load_phases(db)
    items: list[HistoryItemRead] = []
    for phase in phases:
        if week is not None and phase.week_number != week:
            continue
        if phase_id is not None and phase.id != phase_id:
            continue
        for session in phase.sessions:
            current = session_status(session)
            if current == SessionStatus.not_started:
                continue
            if status is not None and current != status:
                continue
            activity_at = _activity_at(session)
            if date_from is not None and (activity_at is None or _local_date(activity_at) < date_from):
                continue
            if date_to is not None and (activity_at is None or _local_date(activity_at) > date_to):
                continue
            items.append(
                HistoryItemRead(
                    session_id=session.id,
                    title=session.title,
                    week_number=phase.week_number,
                    phase_title=phase.title,
                    status=current,
                    activity_at=activity_at,
                    completed_at=session.progress.completed_at if session.progress else None,
                    actual_duration_minutes=session.progress.actual_duration_minutes if session.progress else None,
                    note_excerpt=_note_excerpt(session),
                )
            )
    items.sort(key=lambda item: item.activity_at.isoformat() if item.activity_at else "", reverse=True)
    return items


def get_progress_overview(db: Session) -> ProgressOverviewRead:
    phases = load_phases(db)
    sessions = ordered_sessions(phases)
    statuses = [session_status(session) for session in sessions]
    completed_sessions = sum(status == SessionStatus.completed for status in statuses)
    total_learning_minutes = sum(
        session.progress.actual_duration_minutes or 0
        for session in sessions
        if session.progress and session.progress.status == SessionStatus.completed
    )
    weeks: list[WeekProgressRead] = []
    for phase in phases:
        phase_statuses = [session_status(session) for session in phase.sessions]
        completed = sum(status == SessionStatus.completed for status in phase_statuses)
        minutes = sum(
            session.progress.actual_duration_minutes or 0
            for session in phase.sessions
            if session.progress and session.progress.status == SessionStatus.completed
        )
        weeks.append(
            WeekProgressRead(
                week_number=phase.week_number,
                title=phase.title,
                status=derive_phase_status(phase_statuses),
                completed_sessions=completed,
                total_sessions=len(phase_statuses),
                progress_percent=completion_percent(completed, len(phase_statuses)),
                learning_minutes=minutes,
            )
        )
    return ProgressOverviewRead(
        progress_percent=completion_percent(completed_sessions, len(sessions)),
        completed_sessions=completed_sessions,
        total_sessions=len(sessions),
        total_learning_minutes=total_learning_minutes,
        total_learning_hours=learning_hours(total_learning_minutes),
        weeks=weeks,
    )
