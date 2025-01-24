from sqlmodel import Session, select

from backend.database.schema import DBAccount
from backend.exceptions import EntityNotFound