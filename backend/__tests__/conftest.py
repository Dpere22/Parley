import pytest
from sqlmodel import Session, StaticPool, create_engine
from starlette.testclient import TestClient

from backend import app
from backend.database.schema import *
from backend.dependencies import get_session


@pytest.fixture
def session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture
def account_data():
    return {
        1: {"id": 1, "username": "jamaron", "email": "jm@jm.com", "hashed_password": "123"},
        2: {"id": 2, "username": "loldleman", "email": "lm@lm.com", "hashed_password": "456"}
    }

@pytest.fixture
def chat_data():
    return {
        1: {"id": 1, "name": "gamers", "owner_id": 1},
        2: {"id": 2, "name": "theboys", "owner_id": 2},
    }

@pytest.fixture
def setup_db(session, account_data, chat_data):
    for account in account_data.values():
        session.add(DBAccount(**account))
    for chat in chat_data.values():
        session.add(DBChat(**chat))
    session.commit()

@pytest.fixture
def client(session):
    def _get_session_override():
        return session

    app.dependency_overrides[get_session] = _get_session_override
    yield TestClient(app)
    app.dependency_overrides.clear()

