"""PonyExpress backend API application.

Args:
    app (FastAPI): The FastAPI application
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.dependencies import create_db_tables

from backend.routers.accounts import accounts_router
from backend.routers.chats import chats_router



@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_tables()
    yield


app = FastAPI(
    title="<your API title>",
    summary="<your API summary>",
    lifespan=lifespan,
)

for router in [accounts_router, chats_router]:
    app.include_router(router)



