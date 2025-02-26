from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    app_title: str
    app_description: str
    db_url: str
    jwt_algorithm: str
    jwt_cookie_key: str
    jwt_duration: int
    jwt_issuer: str
    jwt_secret_key: str

settings = Settings(
    app_title = "pony-express",
    app_description = "API to manage pony express",
    db_url = "sqlite:///db.sqlite3",
    jwt_algorithm = "HS256",
    jwt_cookie_key = "pony_express_token",
    jwt_duration = 3600,
    jwt_issuer = "127.0.0.1",
    jwt_secret_key=os.environ.get("JWT_SECRET_KEY", default = "jwt-dev-key"),
)