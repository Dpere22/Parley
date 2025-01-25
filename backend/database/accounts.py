from sqlmodel import Session, select

from backend.database.schema import DBAccount
from backend.exceptions import EntityNotFound

def get_all(session: Session) -> list[DBAccount]:
    stmt = select(DBAccount)
    results = session.exec(stmt)
    return list(results)

def get_by_id(session: Session, account_id: int) -> DBAccount:
    account = session.get(DBAccount, account_id)
    if account is None:
        raise EntityNotFound("account", account_id)
    return account

