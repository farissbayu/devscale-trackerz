from sqlmodel import Session, select

from app.models import LearningPhase, LearningSession, SessionProgress
from app.seed.data import ESTIMATED_DURATION_MINUTES, WEEKS
from app.seed.notevault import MILESTONE_OBJECTIVES, NOTEVAULT_MILESTONES
from app.seed.sources import SOURCE_URLS

REGULAR_TOPICS = ["Core concepts", "Hands-on practice", "Reflection"]
MICRO_TOPICS = ["Scope", "Build", "Demo"]

CONTENT_FIELDS = ("title", "description", "learning_objectives", "topics", "expected_deliverable")


def _entries(week_number: int, week: dict) -> list[dict]:
    entries = [
        {
            "title": title,
            "description": description,
            "learning_objectives": [
                f"Explain the key ideas behind {title}.",
                "Apply the concept in a hands-on exercise.",
                "Write down what is still unclear for review.",
            ],
            "topics": REGULAR_TOPICS,
            "expected_deliverable": f"A working exercise or written notes covering: {title}",
            "source_url": SOURCE_URLS.get(title, ""),
        }
        for title, description in week["sessions"]
    ]
    milestone = NOTEVAULT_MILESTONES[week_number]
    entries.append(
        {
            "title": f"NoteVault W{week_number}: {milestone['name']}",
            "description": milestone["description"],
            "learning_objectives": list(MILESTONE_OBJECTIVES),
            "topics": MICRO_TOPICS,
            "expected_deliverable": milestone["deliverable"],
            "source_url": "",
        }
    )
    return entries


def seed_database(db: Session) -> None:
    """Create or refresh curriculum content. Never touches progress rows, user notes, or user-edited links."""
    for week_number, week in enumerate(WEEKS, start=1):
        phase = db.exec(
            select(LearningPhase).where(LearningPhase.week_number == week_number)
        ).first()
        if phase is None:
            phase = LearningPhase(
                week_number=week_number,
                title=week["title"],
                description=week["description"],
                order_index=week_number,
            )
            db.add(phase)
            db.flush()

        for order_index, entry in enumerate(_entries(week_number, week), start=1):
            session = db.exec(
                select(LearningSession).where(
                    LearningSession.phase_id == phase.id,
                    LearningSession.order_index == order_index,
                )
            ).first()
            if session is None:
                db.add(
                    LearningSession(
                        **entry,
                        phase_id=phase.id,
                        order_index=order_index,
                        estimated_duration_minutes=ESTIMATED_DURATION_MINUTES,
                    )
                )
                continue

            changed = False
            for field in CONTENT_FIELDS:
                if getattr(session, field) != entry[field]:
                    setattr(session, field, entry[field])
                    changed = True
            # Only fill a missing default; never overwrite a link the user saved themselves.
            if not session.source_url and entry["source_url"]:
                session.source_url = entry["source_url"]
                changed = True
            if changed:
                db.add(session)

    missing_progress = db.exec(
        select(LearningSession)
        .outerjoin(SessionProgress, SessionProgress.session_id == LearningSession.id)
        .where(SessionProgress.id.is_(None))
    ).all()
    for session in missing_progress:
        db.add(SessionProgress(session_id=session.id))

    db.commit()
