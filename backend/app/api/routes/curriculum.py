from fastapi import APIRouter

from app.api.deps import SessionDep
from app.schemas import PhaseRead
from app.services.curriculum import get_phase, load_phases, phase_read

router = APIRouter(prefix="/phases", tags=["curriculum"])


@router.get("", response_model=list[PhaseRead])
def list_phases(db: SessionDep) -> list[PhaseRead]:
    return [phase_read(phase) for phase in load_phases(db)]


@router.get("/{phase_id}", response_model=PhaseRead)
def read_phase(phase_id: int, db: SessionDep) -> PhaseRead:
    return get_phase(db, phase_id)
