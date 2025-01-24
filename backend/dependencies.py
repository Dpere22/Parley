"""Dependencies for the backend API.

Args:
    engine (sqlachemy.engine.Engine): The database engine
"""

from sqlmodel import SQLModel, create_engine

from backend.database.schema import *



_db_filename = "backend/database/development.db"
_db_url = f"sqlite:///{_db_filename}"
_connect_args = {"check_same_thread": False}
engine = create_engine(_db_url, echo=True)


def create_db_tables():
    SQLModel.metadata.create_all(engine)
