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

from backend.exceptions import EntityNotFound



@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_tables()
    yield


app = FastAPI(
    title="<your API title>",
    summary="<your API summary>",
    lifespan=lifespan,
)

@app.exception_handler(EntityNotFound)
def handle_not_found(request: Request, exception: EntityNotFound):
    return exception.response()

for router in [accounts_router, chats_router]:
    app.include_router(router)



