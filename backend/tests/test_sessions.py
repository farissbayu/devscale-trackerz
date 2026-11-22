from datetime import date, timedelta

import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.models import LearningSession, SessionProgress, SessionStatus
from app.seed import seed_database
from app.seed.data import WEEKS
from app.seed.sources import SOURCE_URLS


def first_session_id(client) -> int:
    phases = client.get("/api/phases").json()
    return phases[0]["sessions"][0]["id"]


def test_seed_curriculum(client) -> None:
    phases = client.get("/api/phases").json()
    assert len(phases) == 16
    assert sum(len(phase["sessions"]) for phase in phases) == 58
    assert all(
        session["estimated_duration_minutes"] == 90
        for phase in phases
        for session in phase["sessions"]
    )
    assert phases[0]["week_number"] == 1
    assert phases[0]["sessions"][0]["status"] == "not_started"
    assert phases[0]["sessions"][0]["learning_objectives"]
    assert phases[0]["sessions"][-1]["title"].startswith("NoteVault W1:")
    assert phases[-1]["sessions"][-1]["title"].startswith("NoteVault W16:")
    assert phases[0]["sessions"][-1]["topics"] == ["Scope", "Build", "Demo"]
    assert all(
        "DONE WHEN" in session["description"] and len(session["description"]) > 400
        for phase in phases
        for session in phase["sessions"]
        if session["title"].startswith("NoteVault")
    )
    regular = [
        session
        for phase in phases
        for session in phase["sessions"]
        if not session["title"].startswith("NoteVault")
    ]
    assert len(regular) == 42
    assert all(session["source_url"].startswith("https://") for session in regular)
    assert phases[0]["sessions"][-1]["source_url"] == ""


def test_dashboard_starts_at_week_one(client) -> None:
    dashboard = client.get("/api/dashboard").json()
    assert dashboard["overall"]["progress_percent"] == 0.0
    assert dashboard["overall"]["total_sessions"] == 58
    assert dashboard["overall"]["completed_phases"] == 0
    assert dashboard["current_phase"]["week_number"] == 1
    assert dashboard["next_session"]["title"].startswith("Introduction and Learn about the Basic of LLM")
    assert dashboard["curriculum_completed"] is False


def test_start_then_complete_session(client) -> None:
    session_id = first_session_id(client)

    started = client.post(f"/api/sessions/{session_id}/start")
    assert started.status_code == 200
    body = started.json()
    assert body["status"] == "in_progress"
    assert body["started_at"] is not None
    assert body["completed_at"] is None

    completed = client.post(
        f"/api/sessions/{session_id}/complete",
        json={
            "actual_duration_minutes": 75,
            "what_i_learned": "LLM basics",
            "what_i_understand": "Tokens",
            "what_i_dont_understand": "Context limits",
            "implementation_notes": "Called the API",
        },
    )
    assert completed.status_code == 200
    body = completed.json()
    assert body["status"] == "completed"
    assert body["completed_at"] is not None
    assert body["actual_duration_minutes"] == 75
    assert body["what_i_learned"] == "LLM basics"

    dashboard = client.get("/api/dashboard").json()
    assert dashboard["overall"]["completed_sessions"] == 1
    assert dashboard["overall"]["progress_percent"] == 1.7
    assert dashboard["overall"]["total_learning_minutes"] == 75
    assert dashboard["overall"]["total_learning_hours"] == 1.2
    assert dashboard["counts"]["in_progress"] == 0
    assert dashboard["next_session"]["title"].startswith("Python - Variables")
    assert dashboard["recent_activity"][0]["session_id"] == session_id

    phase = client.get("/api/phases").json()[0]
    assert phase["progress_percent"] == 25.0
    assert phase["status"] == "in_progress"


def test_complete_without_start_records_start_time(client) -> None:
    session_id = first_session_id(client)
    response = client.post(
        f"/api/sessions/{session_id}/complete", json={"actual_duration_minutes": 90}
    )
    body = response.json()
    assert response.status_code == 200
    assert body["started_at"] is not None
    assert body["status"] == "completed"


def test_duplicate_completion_is_rejected(client) -> None:
    session_id = first_session_id(client)
    client.post(f"/api/sessions/{session_id}/complete", json={"actual_duration_minutes": 90})
    again = client.post(
        f"/api/sessions/{session_id}/complete", json={"actual_duration_minutes": 90}
    )
    assert again.status_code == 409
    start_again = client.post(f"/api/sessions/{session_id}/start")
    assert start_again.status_code == 409


def test_invalid_duration_is_rejected(client) -> None:
    session_id = first_session_id(client)
    for duration in (0, -5, 1441):
        response = client.post(
            f"/api/sessions/{session_id}/complete", json={"actual_duration_minutes": duration}
        )
        assert response.status_code == 422


def test_save_notes_without_changing_status(client) -> None:
    session_id = first_session_id(client)
    response = client.patch(
        f"/api/sessions/{session_id}/notes",
        json={"what_i_understand": "Enough to continue"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "not_started"
    assert body["what_i_understand"] == "Enough to continue"


def test_reset_clears_status_but_keeps_notes(client) -> None:
    session_id = first_session_id(client)
    client.post(
        f"/api/sessions/{session_id}/complete",
        json={"actual_duration_minutes": 60, "what_i_learned": "A lot"},
    )
    reset = client.post(f"/api/sessions/{session_id}/reset")
    body = reset.json()
    assert body["status"] == "not_started"
    assert body["started_at"] is None
    assert body["completed_at"] is None
    assert body["actual_duration_minutes"] is None
    assert body["what_i_learned"] == "A lot"


def test_skipped_session_is_not_completed(client) -> None:
    session_id = first_session_id(client)
    skipped = client.post(f"/api/sessions/{session_id}/skip")
    assert skipped.status_code == 200
    assert skipped.json()["status"] == "skipped"

    dashboard = client.get("/api/dashboard").json()
    assert dashboard["overall"]["completed_sessions"] == 0
    assert dashboard["overall"]["progress_percent"] == 0.0
    assert dashboard["counts"]["skipped"] == 1
    assert dashboard["next_session"]["title"].startswith("Python - Variables")

    history = client.get("/api/history").json()
    assert history[0]["session_id"] == session_id
    assert history[0]["status"] == "skipped"


def test_completed_session_cannot_be_skipped(client) -> None:
    session_id = first_session_id(client)
    client.post(f"/api/sessions/{session_id}/complete", json={"actual_duration_minutes": 30})
    assert client.post(f"/api/sessions/{session_id}/skip").status_code == 409


def test_unknown_session_returns_404(client) -> None:
    assert client.get("/api/sessions/999999").status_code == 404
    assert client.post("/api/sessions/999999/start").status_code == 404
    assert client.get("/api/phases/999999").status_code == 404


def test_history_filters(client) -> None:
    phases = client.get("/api/phases").json()
    session_id = phases[0]["sessions"][0]["id"]
    client.post(f"/api/sessions/{session_id}/complete", json={"actual_duration_minutes": 45})

    assert len(client.get("/api/history").json()) == 1
    assert client.get("/api/history", params={"week": 1}).json()
    assert client.get("/api/history", params={"week": 2}).json() == []
    assert len(client.get("/api/history", params={"status": "completed"}).json()) == 1
    assert client.get("/api/history", params={"status": "in_progress"}).json() == []
    assert client.get("/api/history", params={"phase_id": phases[0]["id"]}).json()
    assert client.get("/api/history", params={"date_from": str(date.today())}).json()
    future = str(date.today() + timedelta(days=1))
    assert client.get("/api/history", params={"date_from": future}).json() == []


def test_progress_overview(client) -> None:
    session_id = first_session_id(client)
    client.post(f"/api/sessions/{session_id}/complete", json={"actual_duration_minutes": 90})
    overview = client.get("/api/progress").json()
    assert overview["completed_sessions"] == 1
    assert overview["total_sessions"] == 58
    assert overview["progress_percent"] == 1.7
    assert overview["total_learning_hours"] == 1.5
    assert len(overview["weeks"]) == 16
    assert overview["weeks"][0]["progress_percent"] == 25.0
    assert overview["weeks"][0]["learning_minutes"] == 90
    assert overview["weeks"][1]["progress_percent"] == 0.0


def test_one_progress_per_session(db_session: Session) -> None:
    session = db_session.exec(select(LearningSession).limit(1)).one()
    db_session.add(SessionProgress(session_id=session.id))
    with pytest.raises(IntegrityError):
        db_session.commit()

def test_save_learning_source(client) -> None:
    session_id = first_session_id(client)
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    response = client.patch(f"/api/sessions/{session_id}/source", json={"source_url": url})
    assert response.status_code == 200
    assert response.json()["source_url"] == url

    # Persisted in the curriculum read model, not just the response.
    phases = client.get("/api/phases").json()
    assert phases[0]["sessions"][0]["source_url"] == url

    cleared = client.patch(f"/api/sessions/{session_id}/source", json={"source_url": "  "})
    assert cleared.status_code == 200
    assert cleared.json()["source_url"] == ""


def test_invalid_source_url_is_rejected(client) -> None:
    session_id = first_session_id(client)
    for value in ("not-a-url", "javascript:alert(1)", "ftp://example.com/file"):
        response = client.patch(f"/api/sessions/{session_id}/source", json={"source_url": value})
        assert response.status_code == 422

def test_every_regular_topic_has_a_seeded_video() -> None:
    titles = [title for week in WEEKS for title, _ in week["sessions"]]
    assert len(titles) == 42
    assert set(titles) == set(SOURCE_URLS)
    assert all(url.startswith("https://www.youtube.com/watch?v=") for url in SOURCE_URLS.values())


def test_reseed_keeps_user_saved_source(db_session: Session) -> None:
    session = db_session.exec(
        select(LearningSession).where(LearningSession.title.like("Introduction and Learn%"))
    ).one()
    session.source_url = "https://example.com/my-own-link"
    db_session.add(session)
    db_session.commit()

    seed_database(db_session)

    db_session.expire_all()
    refreshed = db_session.get(LearningSession, session.id)
    assert refreshed is not None
    assert refreshed.source_url == "https://example.com/my-own-link"

def test_save_and_clear_video_timestamp(client) -> None:
    session_id = first_session_id(client)
    response = client.patch(
        f"/api/sessions/{session_id}/timestamp", json={"seconds": 754}
    )
    assert response.status_code == 200
    assert response.json()["video_timestamp_seconds"] == 754

    # Persisted in the curriculum read model.
    phases = client.get("/api/phases").json()
    assert phases[0]["sessions"][0]["video_timestamp_seconds"] == 754

    cleared = client.patch(
        f"/api/sessions/{session_id}/timestamp", json={"seconds": None}
    )
    assert cleared.status_code == 200
    assert cleared.json()["video_timestamp_seconds"] is None
    assert cleared.json()["status"] == "not_started"


def test_invalid_video_timestamp_is_rejected(client) -> None:
    session_id = first_session_id(client)
    for value in (-1, 86401):
        response = client.patch(
            f"/api/sessions/{session_id}/timestamp", json={"seconds": value}
        )
        assert response.status_code == 422

def test_session_detail_exposes_next_material(client) -> None:
    phases = client.get("/api/phases").json()
    first_id = phases[0]["sessions"][0]["id"]
    detail = client.get(f"/api/sessions/{first_id}").json()
    assert detail["next_session_id"] == phases[0]["sessions"][1]["id"]
    assert detail["next_session_title"].startswith("Python - Variables")

    last_id = phases[-1]["sessions"][-1]["id"]
    last = client.get(f"/api/sessions/{last_id}").json()
    assert last["next_session_id"] is None
    assert last["next_session_title"] is None
