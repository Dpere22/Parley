"""PonyExpress backend API application.

Args:
    app (FastAPI): The FastAPI application
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.requests import Request

from backend.dependencies import create_db_tables

from backend.routers.accounts import accounts_router
from backend.routers.chats import chats_router

from backend.exceptions import EntityNotFound, DuplicateEntityValue



@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_tables()
    yield


app = FastAPI(
    title="PonyExpress Backend",
    summary="Get info from database",
    lifespan=lifespan,
)

@app.exception_handler(EntityNotFound)
def handle_not_found(request: Request, exception: EntityNotFound):
    return exception.response()

@app.exception_handler(DuplicateEntityValue)
def handle_duplicate_value(request: Request, exception: DuplicateEntityValue):
    return exception.response()
for router in [accounts_router, chats_router]:
    app.include_router(router)



