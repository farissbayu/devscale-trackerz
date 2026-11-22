from fastapi import APIRouter

from app.api.deps import SessionDep
from app.schemas import (
    CompleteSessionRequest,
    NotesPayload,
    SessionDetailRead,
    SessionSourcePayload,
    VideoTimestampPayload,
)
from app.services import sessions as session_service
from app.services.curriculum import get_session_detail

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("/{session_id}", response_model=SessionDetailRead)
def read_session(session_id: int, db: SessionDep) -> SessionDetailRead:
    return get_session_detail(db, session_id)


@router.post("/{session_id}/start", response_model=SessionDetailRead)
def start_session(session_id: int, db: SessionDep) -> SessionDetailRead:
    return session_service.start_session(db, session_id)


@router.post("/{session_id}/complete", response_model=SessionDetailRead)
def complete_session(
    session_id: int, payload: CompleteSessionRequest, db: SessionDep
) -> SessionDetailRead:
    return session_service.complete_session(db, session_id, payload)


@router.post("/{session_id}/skip", response_model=SessionDetailRead)
def skip_session(session_id: int, db: SessionDep) -> SessionDetailRead:
    return session_service.skip_session(db, session_id)


@router.post("/{session_id}/reset", response_model=SessionDetailRead)
def reset_session(session_id: int, db: SessionDep) -> SessionDetailRead:
    return session_service.reset_session(db, session_id)


@router.patch("/{session_id}/source", response_model=SessionDetailRead)
def update_source(
    session_id: int, payload: SessionSourcePayload, db: SessionDep
) -> SessionDetailRead:
    return session_service.save_source(db, session_id, payload)


@router.patch("/{session_id}/timestamp", response_model=SessionDetailRead)
def update_timestamp(
    session_id: int, payload: VideoTimestampPayload, db: SessionDep
) -> SessionDetailRead:
    return session_service.save_timestamp(db, session_id, payload)


@router.patch("/{session_id}/notes", response_model=SessionDetailRead)
def update_notes(session_id: int, payload: NotesPayload, db: SessionDep) -> SessionDetailRead:
    return session_service.save_notes(db, session_id, payload)
