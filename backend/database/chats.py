from sqlmodel import Session, select

from backend.database.schema import DBChat, DBMessage, DBChatMembership, DBAccount
from backend.models import ChatCreate
from backend.exceptions import EntityNotFound, DuplicateEntityValue

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

def create_chat(session: Session, chat: ChatCreate) -> DBChat:
    chat_name = chat.name
    owner_id = chat.owner_id
    owner = _validate_user_exists(session, owner_id)
    if owner is None:
        raise EntityNotFound("user", owner_id)
    if _validate_chat_exists(session, chat_name) is not None:
        raise DuplicateEntityValue(chat_name)
    db_chat = DBChat(
        owner_id=owner_id,
        name=chat_name,
        owner=owner
    )
    session.add(db_chat)
    session.commit()
    return db_chat



def _validate_user_exists(session: Session, user_id: int) -> DBAccount:
    stmt = select(DBAccount).where(DBAccount.id == user_id)
    result = session.exec(stmt).first()
    return result

def _validate_chat_exists(session: Session, chat_name: str) -> DBChat:
    stmt = select(DBChat).where(DBChat.name == chat_name)
    result = session.exec(stmt).first()
    return result