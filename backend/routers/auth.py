from typing import Annotated

from fastapi import APIRouter, Form

from backend.database.auth import *
from backend.dependencies import DBSession
from backend.models import User, AccessToken
from backend.settings import settings

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/registration", status_code=201)
def register_new_user(session: DBSession, registration: Annotated[Registration, Form()]) -> User:
    return User(**create_user(session, registration).model_dump())

@auth_router.post("/token", response_model=AccessToken)
def get_token(session: DBSession, form: Annotated[Login, Form()]) -> AccessToken:
    token = generate_token(session, form)
    return AccessToken(access_token=token, token_type="bearer")

@auth_router.post("/web/login", status_code=204)
def login(response: Response, session: DBSession, form: Annotated[Login, Form()]) -> None:
    token = generate_token(session, form)
    response.set_cookie(
        settings.jwt_cookie_key, token, httponly=True)

@auth_router.post("/web/logout", status_code=204, dependencies=[Depends(get_current_user)])
def logout(response: Response) -> None:
    response.delete_cookie(settings.jwt_cookie_key)