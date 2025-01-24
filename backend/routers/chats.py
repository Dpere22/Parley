from fastapi import APIRouter

from backend.database import chats as chats_db
from backend.database.schema import DBChat
from backend.dependencies import DBSession
from backend.models import Chat

chats_router = APIRouter(prefix="/chats", tags=["chats"])

@chats_router.get("/")
def chats():
    pass

@chats_router.get("/{chat_id}", response_model=Chat)
def get_chat(session: DBSession, chat_id: int) -> DBChat:
    return chats_db.get_by_id(session, chat_id)

@chats_router.get("/{chat_id}/messages")
def messages(chat_id: int):
    pass

@chats_router.get("/chats/{chat_id}/accounts")
def chat_accounts(chat_id: int):
    pass
