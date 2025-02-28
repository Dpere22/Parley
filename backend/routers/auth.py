from typing import Annotated

from fastapi import APIRouter, Form

from backend.database.auth import *
from backend.dependencies import DBSession
from backend.models import User, AccessToken
from backend.settings import settings

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/registration",
                  status_code=201,
                  response_model=User,
                  summary="Register a new user",
                  response_description="User that was created",
                  responses={
                      422: {
                          "model": Err,
                          "description": "Account with username or email already exists"
                      }
                  })
def register_new_user(session: DBSession, registration: Annotated[Registration, Form()]) -> User:
    return User(**create_user(session, registration).model_dump())

@auth_router.post("/token",
                  response_model=AccessToken,
                  summary="Obtain an access token",
                  response_description="The access token",
                  status_code=200,
                  responses={
                      401: {"model": Err, "description": "Invalid username or password"},
                  })
def get_token(session: DBSession, form: Annotated[Login, Form()]) -> AccessToken:
    token = generate_token(session, form)
    return AccessToken(access_token=token, token_type="bearer")

@auth_router.post("/web/login",
                  status_code=204,
                  summary="Obtain an access token as a cookie and login",
                  responses={
                      401: {"model": Err, "description": "Invalid username or password"},
                  })
def login(response: Response, session: DBSession, form: Annotated[Login, Form()]) -> None:
    token = generate_token(session, form)
    response.set_cookie(
        settings.jwt_cookie_key, token, httponly=True)

@auth_router.post("/web/logout",
                  status_code=204,
                  summary="logout and remove access cookie",
                  responses={
                      403: {"model": Err, "description": "You are not logged in"},
                  },
                  dependencies=[Depends(get_current_user)])
def logout(response: Response) -> None:
    response.delete_cookie(settings.jwt_cookie_key)