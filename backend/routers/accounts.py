from fastapi import APIRouter, Depends

from backend.database import accounts as accounts_db
from backend.database.auth import get_current_user
from backend.database.schema import DBAccount
from backend.dependencies import DBSession
from backend.models import Account, Accounts, User
from backend.exceptions import Err

accounts_router = APIRouter(prefix="/accounts", tags=["accounts"])

@accounts_router.get("/",
                     response_model=Accounts,
                     summary="Get all accounts",
                     response_description="Number of accounts and all account objects")
def get_accounts(session: DBSession) -> dict[str, dict[str, int] | list[DBAccount]]:
    accounts = accounts_db.get_all(session)
    metadata = len(accounts)
    return {"metadata": {"count": metadata}, "accounts": accounts}

@accounts_router.get("/{account_id}",
                     response_model=Account,
                     summary="Get account by id",
                     response_description="Account object",
                     responses={
                         404: {
                             "model": Err,
                             "description": "Account not found"
                         }
                     })
def get_account(session: DBSession, account_id: int) -> DBAccount:
    return accounts_db.get_by_id(session, account_id)

@accounts_router.post("/me", dependencies=[Depends(get_current_user)])
def get_me(session: DBSession) -> dict:
    return {"message": "test!"}