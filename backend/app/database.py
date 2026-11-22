from collections.abc import Iterator

from sqlmodel import Session, create_engine

from app.config import get_settings

settings = get_settings()

# SQLite connections are shared across FastAPI's threadpool, so they must allow cross-thread use.
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args, pool_pre_ping=True)


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
