from sqlmodel import Session, select

from backend.database.schema import DBChat, DBMessage, DBChatMembership, DBAccount
from backend.exceptions import *
from backend.models import ChatCreate, ChatUpdate, CreateMessage, UpdateMessage, AddAccountToChat


def get_all(session: Session) -> list[DBChat]:
    stmt = select(DBChat)
    results = session.exec(stmt)
    return list(results)

def get_by_id(session: Session, chat_id: int) -> DBChat:
    chat = session.get(DBChat, chat_id).first()
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

def create_chat(session: Session, chat: ChatCreate, user: DBAccount) -> DBChat:
    chat_name = chat.name
    owner_id = chat.owner_id
    owner = _validate_user_exists(session, owner_id)
    if owner_id != user.id:
        raise AccessDeniedException
    if owner is None:
        raise EntityNotFound("account", owner_id)
    if _validate_chat_exists(session, chat_name) is not None:
        raise DuplicateEntityValue("chat", "name", chat_name)
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
        if _validate_chat_exists(session, update.name) is not None and chat.name != update.name:
            raise DuplicateEntityValue("chat", "name", update.name)
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

def add_chat_message(session: Session, chat_id: int, message: CreateMessage, user: DBAccount) -> DBMessage:
    chat = get_by_id(session, chat_id)
    if message.account_id != user.id: raise AccessDeniedException
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

def update_chat_message(session: Session, chat_id: int, message_id: int, update_message: UpdateMessage) -> DBMessage:
    get_by_id(session, chat_id) #for checking if chat exists
    message = _validate_message_in_chat(session, chat_id, message_id)
    message.text = update_message.text
    session.add(message)
    session.commit()
    session.refresh(message)
    return message

def delete_chat_message(session: Session, chat_id: int, message_id: int):
    get_by_id(session, chat_id)
    message = _validate_message_in_chat(session, chat_id, message_id)
    session.delete(message)
    session.commit()

def add_account_to_chat(session: Session, chat_id: int, response_account: AddAccountToChat) -> tuple[bool, DBChatMembership]:
    account_id = response_account.account_id
    account = _validate_user_exists(session, account_id)
    if account is None:
        raise EntityNotFound("account", account_id)
    get_by_id(session, chat_id) ## make sure chat exists
    members = get_chat_members(session, chat_id)
    if account not in members:
        db_chat_membership = DBChatMembership(
            chat_id=chat_id,
            account_id=account_id,
        )
        session.add(db_chat_membership)
        session.commit()
        return True, db_chat_membership
    else:
        stmt = select(DBChatMembership).where(DBChatMembership.chat_id == chat_id).where(DBChatMembership.account_id == account.id)
        membership = session.exec(stmt).first()
        return False, membership

def delete_account_from_chat(session: Session, chat_id: int, account_id: int):
    chat = get_by_id(session, chat_id)
    _validate_user_in_chat(session, chat_id, account_id)
    if chat.owner_id == account_id:
        raise OwnerRemoval
    messages = session.exec(
        select(DBMessage).where(DBMessage.chat_id == chat_id, DBMessage.account_id == account_id)
    ).all()

    for message in messages:
        message.account_id = None
        session.add(message)
    session.commit()


    stmt = select(DBChatMembership).where(DBChatMembership.chat_id == chat_id).where(
        DBChatMembership.account_id == account_id)
    membership = session.exec(stmt).first()
    session.delete(membership)
    session.commit()


def _validate_message_in_chat(session: Session, chat_id: int, message_id: int):
    stmt = select(DBMessage).where(DBMessage.id == message_id).where(DBMessage.chat_id == chat_id)
    message = session.exec(stmt).first()
    if message is None:
        raise EntityNotFound("message", message_id)
    return message

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

def _validate_chat_exists_by_id(session: Session, chat_id: int) -> DBChat:
    stmt = select(DBChat).where(DBChat.id == chat_id)
    result = session.exec(stmt).first()
    return result