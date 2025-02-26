from datetime import timezone

from fastapi import Depends
from fastapi.security import APIKeyCookie, HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, ExpiredSignatureError

from backend.dependencies import get_session
from backend.models import Registration
from backend.database.schema import *
import bcrypt

from sqlmodel import Session, select
#from sqlalchemy import func

from backend.exceptions import *

from backend.models import Login, Claims

from backend.database.accounts import _get_by_username, get_by_id

from backend.settings import settings

cookie_scheme = APIKeyCookie(name=settings.jwt_cookie_key, auto_error=False)
bearer_scheme = HTTPBearer(auto_error=False)

def create_user(session: Session, form: Registration) -> DBAccount:
    if not check_username_available(session, form.username):
        raise DuplicateEntityValue("account", "username", form.username)
    if not check_email_available(session, form.email):
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

def validate_credentials(user: DBAccount | None, password: str) -> DBAccount:
    if user is None or not _verify_password(password, user.hashed_password):
        raise InvalidCredentials()
    return user


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
    #stmt = select(DBAccount).where(func.lower(DBAccount.email) == email.lower())
    stmt = select(DBAccount).where(DBAccount.email == email)
    user = session.exec(stmt).first()
    return user is None

def generate_claims(user: DBAccount) -> Claims:
    iat = int(datetime.now(timezone.utc).timestamp())
    exp = iat + settings.jwt_duration
    return Claims(
        sub=str(user.id),
        iss = "http://127.0.0.1",
        iat = iat,
        exp=exp,
    )



def generate_token(session: Session, form: Login) -> str:
    user = _get_by_username(session, form.username)
    user = validate_credentials(user, form.password)
    claims = generate_claims(user)
    return jwt.encode(
        claims.model_dump(),
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

def extract_user(session: Session, token:str) -> DBAccount:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        claims = Claims(**payload)
        return get_by_id(session, int(claims.sub))
    except ExpiredSignatureError:
        raise InvalidCredentials()
    except Exception:
        raise InvalidCredentials()



def get_access_token(cookie_token: str | None = Depends(cookie_scheme), bearer_token: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)) -> str:
    if cookie_token is not None:
        return cookie_token
    elif bearer_token is not None:
        return bearer_token.credentials
    else:
        raise NotAuthenticatedNoToken()

def get_current_user(session: Session = Depends(get_session), token: str = Depends(get_access_token)) -> DBAccount:
    return extract_user(session, token)