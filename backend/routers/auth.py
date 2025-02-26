from fastapi import APIRouter, Form, Depends
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from backend.models import Registration, User, AccessToken
from backend.database.auth import *

from backend.dependencies import DBSession


auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/registration", status_code=201)
def register_new_user(session: DBSession, registration: Annotated[Registration, Form()]) -> User:
    return create_user(session, registration)

@auth_router.post("/token", response_model=AccessToken)
def login(session: DBSession, form: Annotated[OAuth2PasswordRequestForm, Depends()]) -> AccessToken:
    user = get_verified_user(session, form.username, form.password)
    return AccessToken(access_token=user.username)