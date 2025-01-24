from sqlmodel import Session, select

from backend.database.schema import DBChat
from backend.exceptions import EntityNotFound

def get_by_id(session: Session, chat_id: int) -> DBChat:
    chat = session.get(DBChat, chat_id)
    if chat is None:
        raise EntityNotFound("chat", chat_id)
    return chat

