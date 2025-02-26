from backend.models import Registration
from backend.database.schema import *
import bcrypt

from sqlmodel import Session, select
from sqlalchemy import func

from backend.exceptions import *


def create_user(session: Session, form: Registration) -> DBAccount:
    if check_username_available(session, form.username) == False:
        raise DuplicateEntityValue("account", "username", form.username)
    if check_email_available(session, form.email) == False:
        raise DuplicateEntityValue("account", "email", form.email)
    hashed_password = _hash_password(form.password)
    user = DBAccount(**form.model_dump(), hashed_password=hashed_password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def _hash_password(password):
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

def _verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )

def get_verified_user(session: Session, username: str, password: str) -> DBAccount:
    stmt = select(DBAccount).where(DBAccount.username == username)
    user = session.exec(stmt).one_or_none()
    if user is not None and _verify_password(password, user.hashed_password):
        return user
    raise InvalidCredentials()

def check_username_available(session: Session, username: str) -> bool:
    stmt = select(DBAccount).where(DBAccount.username == username)
    user = session.exec(stmt).first()
    return user is None

def check_email_available(session: Session, email: str) -> bool:
    stmt = select(DBAccount).where(func.lower(DBAccount.email) == email.lower())
    user = session.exec(stmt).first()
    return user is None
