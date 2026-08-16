from typing import Annotated

from fastapi import APIRouter, Depends, Form

from backend.database import accounts as accounts_db
from backend.database import chats as chats_db
from backend.database.auth import get_current_user
from backend.database.schema import DBAccount, DBChat
from backend.dependencies import DBSession
from backend.models import Account, Accounts, Chats, User, AccountUpdate, PasswordUpdate
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

@accounts_router.get("/me",
                     summary="Get logged in user",
                     response_model=User,
                      responses={
                          403: {
                              "model": Err,
                              "description": "Expired, invalid, or no token"
                          }
                      })
def get_me(user: Annotated[User, Depends(get_current_user)]) -> User:
    return user

@accounts_router.get("/me/chats",
                     response_model=Chats,
                     summary="Get the chats the logged in user is a member of",
                     response_description="Chat count and the caller's chats",
                     responses={
                         403: {
                             "model": Err,
                             "description": "Expired, invalid, or no token"
                         }
                     })
def get_my_chats(session: DBSession, user: Annotated[DBAccount, Depends(get_current_user)]) -> dict[str, dict[str, int] | list[DBChat]]:
    chats = chats_db.get_account_chats(session, user.id)
    return {"metadata": {"count": len(chats)}, "chats": chats}

@accounts_router.put("/me/password",
                     status_code=204,
                     summary="Update logged in user's password",
                     responses={
                         403: {
                             "model": Err,
                             "description": "Expired or invalid, or no token"
                         },
                         401: {
                             "model": Err,
                             "description": "Invalid username or password"
                         }
                     })
def update_password(session: DBSession, form: Annotated[PasswordUpdate, Form()], user: Annotated[DBAccount, Depends(get_current_user)]):
    accounts_db.update_password(form, user, session)

@accounts_router.put("/me",
                     status_code=200,
                     response_model=User,
                     summary="Update logged in user's username or password",
                     responses={
                         403:{
                             "model": Err,
                             "description": "Expired or invalid, or no token"
                         },
                         422:{
                             "model": Err,
                             "description": "Email or username not available"
                         }
                     })
def update_login_in_user(account: AccountUpdate, session: DBSession, user: Annotated[DBAccount, Depends(get_current_user)]) -> User:
    account = accounts_db.update_account(account, user, session)
    return User(**account.model_dump())

@accounts_router.delete("/me",
                        status_code=204,
                        summary="Delete logged in user",
                        responses={
                            403: {
                                "model": Err,
                                "description": "Expired, invalid, or no token"
                            },
                            422:{
                                "model": Err,
                                "description": "Cannot delete owner of a chat"
                            }
                        })
def delete_login_in_user(session: DBSession, user: Annotated[DBAccount, Depends(get_current_user)]):
    return accounts_db.delete_account(session, user)

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



