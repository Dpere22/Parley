from sqlalchemy import func
from sqlmodel import Session, select

from backend.database.schema import DBAccount, DBChat
from backend.exceptions import EntityNotFound, InvalidCredentials, DuplicateEntityValue, OwnerRemoval
from backend.models import AccountUpdate, PasswordUpdate
from backend.database import password as password_utils


def get_all(session: Session) -> list[DBAccount]:
    stmt = select(DBAccount)
    results = session.exec(stmt)
    return list(results)

def get_by_id(session: Session, account_id: int) -> DBAccount:
    account = session.get(DBAccount, account_id)
    if account is None:
        raise EntityNotFound("account", account_id)
    return account

def _get_by_username(session: Session, username: str) -> DBAccount:
    stmt = select(DBAccount).where(DBAccount.username == username)
    account = session.exec(stmt).first()
    if account is None:
        raise InvalidCredentials()
    return account

def get_by_username(session: Session, username: str) -> DBAccount | None:
    """Look up an account without raising when it is absent.

    Login needs the None back rather than an exception, so that it can still spend the
    time verifying a password and not leak which usernames exist.
    """
    stmt = select(DBAccount).where(DBAccount.username == username)
    return session.exec(stmt).first()

def check_username_available(session: Session, username: str) -> bool:
    stmt = select(DBAccount).where(DBAccount.username == username)
    user = session.exec(stmt).first()
    return user is None

def check_email_available(session: Session, email: str) -> bool:
    ## compared case-insensitively on both sides, so an existing Bob@x.com blocks bob@x.com
    stmt = select(DBAccount).where(func.lower(DBAccount.email) == email.lower())
    user = session.exec(stmt).first()
    return user is None

def update_account(update: AccountUpdate, user: DBAccount, session: Session) -> DBAccount:
    if update.username is not None:
        if check_username_available(session, update.username) or user.username == update.username:
            user.username = update.username
        else:
            raise DuplicateEntityValue("account", "username", update.username)
    if update.email is not None:
        if check_email_available(session, update.email) or user.email == update.email:
            user.email = update.email
        else:
            raise DuplicateEntityValue("account", "email", update.email)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def update_password(form: PasswordUpdate, user: DBAccount, session: Session) -> None:
    verified = password_utils.verify_password(form.old_password, user.hashed_password)
    if verified:
        user.hashed_password = password_utils.hash_password(form.new_password)
        session.add(user)
        session.commit()
        session.refresh(user)
    else:
        raise InvalidCredentials()

def delete_account(session: Session, user: DBAccount) -> None:
    stmt = select(DBChat).where(DBChat.owner_id == user.id)
    result = session.exec(stmt).first()
    if result is not None:
        raise OwnerRemoval()
    session.delete(user)
    session.commit()

