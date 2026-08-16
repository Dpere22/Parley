import os
from pathlib import Path

from pydantic_settings import BaseSettings

# Resolved from this file rather than the working directory, so the app opens the
# same database no matter where it is launched from.
_default_db_path = Path(__file__).parent / "database" / "development.db"


class Settings(BaseSettings):
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
    app_title = "pony-express",
    app_description = "API to manage pony express",
    db_url = os.environ.get("DB_URL", default = f"sqlite:///{_default_db_path}"),
    db_echo = os.environ.get("DB_ECHO", default = "").lower() in ("1", "true", "yes"),
    jwt_algorithm = "HS256",
    jwt_cookie_key = "pony_express_token",
    jwt_duration = 3600,
    jwt_issuer = "http://127.0.0.1",
    jwt_secret_key=os.environ.get("JWT_SECRET_KEY", default = "jwt-dev-key"),
)
