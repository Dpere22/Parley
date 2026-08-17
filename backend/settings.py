import os
from pathlib import Path

from pydantic_settings import BaseSettings

# Resolved from this file rather than the working directory, so the app opens the
# same database no matter where it is launched from.
_default_db_path = Path(__file__).parent / "database" / "development.db"


# Signing key used when JWT_SECRET_KEY is unset. Fine for local development, and
# refused outside it - see the check below.
DEV_JWT_SECRET_KEY = "jwt-dev-key"


class Settings(BaseSettings):
    app_env: str
    app_title: str
    app_description: str
    db_url: str
    db_echo: bool
    jwt_algorithm: str
    jwt_cookie_key: str
    jwt_duration: int
    jwt_issuer: str
    jwt_secret_key: str

settings = Settings(
    app_env = os.environ.get("APP_ENV", default = "development"),
    app_title = "parley",
    app_description = "API to manage parley",
    db_url = os.environ.get("DB_URL", default = f"sqlite:///{_default_db_path}"),
    db_echo = os.environ.get("DB_ECHO", default = "").lower() in ("1", "true", "yes"),
    jwt_algorithm = "HS256",
    jwt_cookie_key = "parley_token",
    jwt_duration = 3600,
    jwt_issuer = "http://127.0.0.1",
    jwt_secret_key=os.environ.get("JWT_SECRET_KEY", default = DEV_JWT_SECRET_KEY),
)

# The development key is public in this repository, so anything signed with it can be
# forged by anyone. Failing here is much safer than booting and quietly accepting
# forged tokens, which is what happens when JWT_SECRET_KEY is simply forgotten.
if settings.app_env != "development" and settings.jwt_secret_key == DEV_JWT_SECRET_KEY:
    raise RuntimeError(
        f"JWT_SECRET_KEY must be set when APP_ENV={settings.app_env!r}; "
        "refusing to start with the development signing key."
    )
