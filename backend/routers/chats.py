from fastapi import APIRouter

from backend.database import chats as chats_db
from backend.database.schema import DBChat, DBMessage, DBAccount
from backend.dependencies import DBSession
from backend.exceptions import EntityNotFound
from backend.models import Chat, ChatMessages, ChatAccounts, Chats

chats_router = APIRouter(prefix="/chats", tags=["chats"])

@chats_router.get("/", response_model = Chats)
def chats(session: DBSession) -> dict[str, dict[str, int] | list[DBChat]]:
    all_chats = chats_db.get_all(session)
    metadata = len(all_chats)
    return {"metadata": {"count": metadata}, "chats": all_chats}

@chats_router.get("/{chat_id}", response_model=Chat)
def get_chat(session: DBSession, chat_id: int) -> DBChat:
    chat = chats_db.get_by_id(session, chat_id)
    if chat is None:
        raise EntityNotFound("chat", chat_id)
    return chats_db.get_by_id(session, chat_id)

@chats_router.get("/{chat_id}/messages", response_model = ChatMessages)
def messages(session: DBSession, chat_id: int) -> dict[str, dict[str, int] | list[DBMessage]]:
    chat = chats_db.get_by_id(session, chat_id)
    if chat is None:
        raise EntityNotFound("chat", chat_id)
    all_messages = chats_db.get_messages(session, chat_id)
    metadata = len(all_messages)
    return {"metadata": {"count": metadata}, "messages": all_messages}

@chats_router.get("/{chat_id}/accounts", response_model = ChatAccounts)
def chat_accounts(session: DBSession, chat_id: int) -> dict[str, dict[str, int] | list[DBAccount]]:
    chat = chats_db.get_by_id(session, chat_id)
    if chat is None:
        raise EntityNotFound("chat", chat_id)
    all_members = chats_db.get_chat_members(session, chat_id)
    metadata = len(all_members)
    return {"metadata": {"count": metadata}, "accounts": all_members}
