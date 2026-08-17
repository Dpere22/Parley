import secrets
from datetime import timezone

from fastapi import Depends
from fastapi.security import APIKeyCookie, HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError
from pydantic import ValidationError

from backend.dependencies import get_session
from backend.models import Registration
from backend.database.schema import *

from sqlmodel import Session, select
#from sqlalchemy import func

from backend.exceptions import *

from backend.models import Login, Claims

from backend.database.accounts import get_by_username, get_by_id, check_email_available, check_username_available

from backend.database import password as password_utils

from backend.settings import settings

cookie_scheme = APIKeyCookie(name=settings.jwt_cookie_key, auto_error=False)
bearer_scheme = HTTPBearer(auto_error=False)

def create_user(session: Session, form: Registration) -> DBAccount:
    if not check_username_available(session, form.username):
        raise DuplicateEntityValue("account", "username", form.username)
    if not check_email_available(session, form.email):
        raise DuplicateEntityValue("account", "email", form.email)
    hashed_password = password_utils.hash_password(form.password)
    user = DBAccount(**form.model_dump(), hashed_password=hashed_password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


## Compared against when the named account does not exist, so that an unknown username
## costs the same bcrypt work as a known one. Without this, a caller can tell the two
## apart from response time alone - measured at 190ms versus 2ms before this was added.
_ABSENT_USER_HASH = password_utils.hash_password(secrets.token_urlsafe(32))


def validate_credentials(user: DBAccount | None, password: str) -> DBAccount:
    hashed_password = _ABSENT_USER_HASH if user is None else user.hashed_password
    ## deliberately not short-circuited: the comparison runs either way
    password_matches = password_utils.verify_password(password, hashed_password)
    if user is None or not password_matches:
        raise InvalidCredentials()
    return user


def get_verified_user(session: Session, username: str, password: str) -> DBAccount:
    stmt = select(DBAccount).where(DBAccount.username == username)
    user = session.exec(stmt).one_or_none()
    if user is not None and password_utils.verify_password(password, user.hashed_password):
        return user
    raise InvalidCredentials()


def generate_claims(user: DBAccount) -> Claims:
    iat = int(datetime.now(timezone.utc).timestamp())
    exp = iat + settings.jwt_duration
    return Claims(
        sub=str(user.id),
        iss = settings.jwt_issuer,
        iat = iat,
        exp=exp,
    )

def generate_token(session: Session, form: Login) -> str:
    ## non-raising lookup, so an unknown username still reaches validate_credentials
    ## and pays the same bcrypt cost as a real one
    user = validate_credentials(get_by_username(session, form.username), form.password)
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
            issuer=settings.jwt_issuer,
        )
        claims = Claims(**payload)
        return get_by_id(session, int(claims.sub))
    ## ExpiredSignatureError subclasses JWTError, so it has to be caught first.
    except ExpiredSignatureError:
        raise NotAuthenticatedExpiredToken
    ## Everything a hostile or stale token can realistically trigger: a bad signature,
    ## algorithm or issuer (JWTError); a payload missing claims (ValidationError, which
    ## is not a JWTError); a non-numeric subject (ValueError); or a subject naming an
    ## account that has since been deleted (EntityNotFound). Anything else is a bug in
    ## our own code and should surface as a 500 rather than be relabelled as auth failure.
    except (JWTError, ValidationError, ValueError, EntityNotFound):
        raise InvalidTokenException()



def get_access_token(cookie_token: str | None = Depends(cookie_scheme), bearer_token: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)) -> str:
    if cookie_token is not None:
        return cookie_token
    elif bearer_token is not None:
        return bearer_token.credentials
    else:
        raise NotAuthenticatedNoToken()

def get_current_user(session: Session = Depends(get_session), token: str = Depends(get_access_token)) -> DBAccount:
    return extract_user(session, token)