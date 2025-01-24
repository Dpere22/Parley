"""PonyExpress backend API application.

Args:
    app (FastAPI): The FastAPI application
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.dependencies import create_db_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_tables()
    yield


app = FastAPI(
    title="<your API title>",
    summary="<your API summary>",
    lifespan=lifespan,
)

##Note to me, a routers module would be way better than this
@app.get("/status", response_model=None, status_code=204)
def status():
    pass

@app.get("/accounts")
def accounts():
    pass

@app.get("/accounts/{account_id}")
def get_account(account_id: int):
    pass

@app.get("/chats")
def chats():
    pass

@app.get("/chats/{chat_id}")
def get_chat(chat_id: int):
    pass

@app.get("/chats/{chat_id}/messages")
def messages(chat_id: int):
    pass

@app.get("/chats/{chat_id}/accounts")
def chats_accounts(chat_id: int):
    pass
