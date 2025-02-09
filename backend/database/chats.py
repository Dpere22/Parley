from sqlmodel import Session, select

from backend.database.schema import DBChat, DBMessage, DBChatMembership, DBAccount
from backend.models import ChatCreate, ChatUpdate, CreateMessage
from backend.exceptions import EntityNotFound, DuplicateEntityValue, AccountNotInChat

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
        raise EntityNotFound("account", owner_id)
    if _validate_chat_exists(session, chat_name) is not None:
        raise DuplicateEntityValue(chat_name)
    db_chat = DBChat(
        owner_id=owner_id,
        name=chat_name,
        owner=owner
    )
    session.add(db_chat)
    session.commit()
    db_chat_membership = DBChatMembership(
        chat_id=db_chat.id,
        account_id=owner_id
    )
    session.add(db_chat_membership)
    session.commit()
    return db_chat


def update_chat(session: Session, chat_id: int, update: ChatUpdate) -> DBChat:
    chat = get_by_id(session, chat_id)
    ## Logic for updating chat name if necessary
    if update.name is not None:
        if _validate_chat_exists(session, update.name) is not None:
            raise DuplicateEntityValue(update.name)
        chat.name = update.name
    ## Logic for updating owner id if necessary
    if update.owner_id is not None:
        owner = _validate_user_in_chat(session, chat_id, update.owner_id)
        chat.owner = owner
        chat.owner_id = update.owner_id
    ## Update Database
    session.add(chat)
    session.commit()
    session.refresh(chat)
    return chat

def delete_chat(session: Session, chat_id: int):
    chat = get_by_id(session, chat_id)
    session.delete(chat)
    session.commit()

def add_chat_message(session: Session, chat_id: int, message: CreateMessage) -> DBMessage:
    chat = get_by_id(session, chat_id)
    account = _validate_user_in_chat(session, chat_id, message.account_id)
    db_message = DBMessage(
        text=message.text,
        chat_id=chat_id,
        account_id=message.account_id,
        account = account,
        chat = chat,
    )
    session.add(db_message)
    session.commit()
    return db_message


def _validate_user_in_chat(session: Session, chat_id: int, user_id: int):
    members = get_chat_members(session, chat_id)
    owner = _validate_user_exists(session, user_id)
    if owner is None or owner not in members:
        raise AccountNotInChat(user_id, chat_id)
    return owner

def _validate_user_exists(session: Session, user_id: int) -> DBAccount:
    stmt = select(DBAccount).where(DBAccount.id == user_id)
    result = session.exec(stmt).first()
    return result

def _validate_chat_exists(session: Session, chat_name: str) -> DBChat:
    stmt = select(DBChat).where(DBChat.name == chat_name)
    result = session.exec(stmt).first()
    return result