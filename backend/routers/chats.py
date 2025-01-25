from fastapi import APIRouter

from backend.database import chats as chats_db
from backend.database.schema import DBChat
from backend.dependencies import DBSession
from backend.exceptions import EntityNotFound
from backend.models import Chat, ChatMessages, ChatMembers

chats_router = APIRouter(prefix="/chats", tags=["chats"])

@chats_router.get("/")
def chats(session: DBSession):
    all_chats = chats_db.get_all(session)
    metadata = len(all_chats)
    return {"metadata": metadata, "accounts": all_chats}

@chats_router.get("/{chat_id}", response_model=Chat)
def get_chat(session: DBSession, chat_id: int) -> DBChat:
    chat = chats_db.get_by_id(session, chat_id)
    if chat is None:
        raise EntityNotFound("chat", chat_id)
    return chats_db.get_by_id(session, chat_id)

@chats_router.get("/{chat_id}/messages", response_model = ChatMessages)
def messages(session: DBSession, chat_id: int):
    chat = chats_db.get_by_id(session, chat_id)
    if chat is None:
        raise EntityNotFound("chat", chat_id)
    all_messages = chats_db.get_messages(session, chat_id)
    metadata = len(all_messages)
    return {"metadata": metadata, "messages": all_messages}

@chats_router.get("/chats/{chat_id}/accounts", response_model = ChatMembers)
def chat_accounts(session: DBSession, chat_id: int):
    chat = chats_db.get_by_id(session, chat_id)
    if chat is None:
        raise EntityNotFound("chat", chat_id)
    all_members = chats_db.get_chat_members(session, chat_id)
    metadata = len(all_members)
    return {"metadata": metadata, "members": all_members}
