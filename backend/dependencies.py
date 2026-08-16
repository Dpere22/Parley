"""Dependencies for the backend API.

Args:
    engine (sqlachemy.engine.Engine): The database engine
"""
from typing import Annotated

from fastapi import Depends
from sqlmodel import SQLModel, create_engine, Session


from backend.database.schema import *
from backend.settings import settings


_connect_args = {"check_same_thread": False}
engine = create_engine(
    settings.db_url,
    echo=settings.db_echo,
    connect_args=_connect_args,
)


def create_db_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

DBSession = Annotated[Session, Depends(get_session)]
