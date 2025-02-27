import pytest
from sqlmodel import Session, StaticPool, create_engine
from starlette.testclient import TestClient

from backend import app
from backend.database.schema import *
from backend.dependencies import get_session
from backend.database import auth, accounts

from datetime import datetime

## SETUP SESSION


def hash_password_stub(password: str) -> str:
    return f"hashed_{password}"

def verify_password_stub(password: str, hashed_password: str) -> bool:
    return hash_password_stub(password) == hashed_password


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

## SETUP TEST DATABASE
@pytest.fixture
def account_data():
    return {
        1: {"id": 1, "username": "jamaron", "email": "jm@jm.com", "hashed_password": "hashed_password"},
        2: {"id": 2, "username": "loldleman", "email": "lm@lm.com", "hashed_password": "hashed_password"},
        3: {"id": 3, "username": "john", "email": "cringe@cringe.com", "hashed_password": "hashed_password"},
    }

@pytest.fixture
def chat_data():
    return {
        1: {"id": 1, "name": "gamers", "owner_id": 1},
        2: {"id": 2, "name": "theboys", "owner_id": 2},
    }

@pytest.fixture
def message_data():
    return{
        1: {"id": 1, "text": "hi gamers", "account_id": 1, "chat_id": 1, "created_at": datetime(2025, 1, 25, 5, 19, 49)},
        2: {"id": 2, "text": "hi :3", "account_id": 2, "chat_id": 1, "created_at": datetime(2025, 1, 25, 5, 20, 34)},
        3: {"id": 3, "text": "just me huh", "account_id": 2, "chat_id": 2, "created_at": datetime(2025, 1, 25, 10, 20, 49)},
    }

@pytest.fixture
def chat_membership_data():
    return {
        1: {"account_id": 1, "chat_id": 1},
        2: {"account_id": 2, "chat_id": 1},
        3: {"account_id": 2, "chat_id": 2},
    }

@pytest.fixture
def setup_db(session, account_data, chat_data, message_data, chat_membership_data):
    for account in account_data.values():
        session.add(DBAccount(**account))
    for chat in chat_data.values():
        session.add(DBChat(**chat))
    for message in message_data.values():
        session.add(DBMessage(**message))
    for chat_membership in chat_membership_data.values():
        session.add(DBChatMembership(**chat_membership))
    session.commit()

## SETUP CLIENT
@pytest.fixture
def client(session, monkeypatch):
    def _get_session_override():
        return session

    monkeypatch.setattr(auth, "_hash_password", hash_password_stub)
    monkeypatch.setattr(auth, "_verify_password", verify_password_stub)
    monkeypatch.setattr(accounts, "hash_password", hash_password_stub)
    monkeypatch.setattr(accounts, "verify_password", verify_password_stub)
    app.dependency_overrides[get_session] = _get_session_override
    yield TestClient(app)
    app.dependency_overrides.clear()

