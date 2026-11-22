import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.database import get_session
from app.main import app
from app.seed import seed_database


@pytest.fixture()
def engine():
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as db:
        seed_database(db)
    yield test_engine
    SQLModel.metadata.drop_all(test_engine)
    test_engine.dispose()


@pytest.fixture()
def db_session(engine):
    with Session(engine) as db:
        yield db


@pytest.fixture()
def client(engine):
    def override_get_session():
        with Session(engine) as db:
            yield db

    app.dependency_overrides[get_session] = override_get_session
    # No context manager: the lifespan seed targets the real database, tests seed themselves.
    test_client = TestClient(app)
    yield test_client
    test_client.close()
    app.dependency_overrides.clear()
