from datetime import date

from fastapi import APIRouter, Query

from app.api.deps import SessionDep
from app.models import SessionStatus
from app.schemas import DashboardRead, HistoryItemRead, ProgressOverviewRead
from app.services.curriculum import get_dashboard, get_history, get_progress_overview

router = APIRouter(tags=["insights"])


@router.get("/dashboard", response_model=DashboardRead)
def read_dashboard(db: SessionDep) -> DashboardRead:
    return get_dashboard(db)


@router.get("/history", response_model=list[HistoryItemRead])
def read_history(
    db: SessionDep,
    week: int | None = Query(default=None, ge=1, le=52),
    phase_id: int | None = Query(default=None, ge=1),
    status: SessionStatus | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> list[HistoryItemRead]:
    return get_history(
        db, week=week, phase_id=phase_id, status=status, date_from=date_from, date_to=date_to
    )


@router.get("/progress", response_model=ProgressOverviewRead)
def read_progress(db: SessionDep) -> ProgressOverviewRead:
    return get_progress_overview(db)
