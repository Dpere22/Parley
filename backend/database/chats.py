from sqlmodel import Session, select

from backend.database.schema import DBChat, DBMessage, DBChatMembership, DBAccount
from backend.exceptions import EntityNotFound

def get_all(session: Session) -> list[DBChat]:
    stmt = select(DBChat)
    results = session.exec(stmt)
    return list(results)

def get_by_id(session: Session, chat_id: int) -> DBChat:
    chat = session.get(DBChat, chat_id)
    if chat is None:
        raise EntityNotFound("chat", chat_id)
    return chat

def get_messages(session: Session, chat_id: int) -> list[DBMessage]:
    stmt = select(DBMessage).where(DBMessage.chat_id == chat_id)
    results = session.exec(stmt)
    return list(results)

def get_chat_members(session: Session, chat_id: int) -> list[DBAccount]:
    stmt = select(DBAccount).join(DBChatMembership, DBChatMembership.account_id == DBAccount.id).where(DBChatMembership.chat_id == chat_id)
    results = session.exec(stmt)
    return list(results)