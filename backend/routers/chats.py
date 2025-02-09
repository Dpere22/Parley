from fastapi import APIRouter, Response
from starlette.responses import JSONResponse

from backend.database import chats as chats_db
from backend.database.schema import DBChat, DBMessage, DBAccount
from backend.dependencies import DBSession
from backend.exceptions import EntityNotFound, Err
from backend.models import *
chats_router = APIRouter(prefix="/chats", tags=["chats"])


@chats_router.get("/",
                  response_model = Chats,
                  summary="Get all chats",
                  response_description="Chat count, and all chats",)
def chats(session: DBSession) -> dict[str, dict[str, int] | list[DBChat]]:
    all_chats = chats_db.get_all(session)
    metadata = len(all_chats)
    return {"metadata": {"count": metadata}, "chats": all_chats}

@chats_router.get("/{chat_id}",
                  response_model=Chat,
                  summary="Get a chat by id",
                  responses={
                         404: {
                             "model": Err,
                             "description": "Chat not found"
                         }
                     })
def get_chat(session: DBSession, chat_id: int) -> DBChat:
    chat = chats_db.get_by_id(session, chat_id)
    if chat is None:
        raise EntityNotFound("chat", chat_id)
    return chats_db.get_by_id(session, chat_id)

@chats_router.get("/{chat_id}/messages",
                  response_model = ChatMessages,
                  summary="Get all messages in a specified chat",
                  response_description="Message count and all messages objects",
                  responses={
                         404: {
                             "model": Err,
                             "description": "Chat not found"
                         }
                     })
def messages(session: DBSession, chat_id: int) -> dict[str, dict[str, int] | list[DBMessage]]:
    chat = chats_db.get_by_id(session, chat_id)
    if chat is None:
        raise EntityNotFound("chat", chat_id)
    all_messages = chats_db.get_messages(session, chat_id)
    metadata = len(all_messages)
    return {"metadata": {"count": metadata}, "messages": all_messages}

@chats_router.get("/{chat_id}/accounts",
                  response_model = ChatAccounts,
                  summary="Get all accounts in a chat",
                  response_description="Account count, and all accounts objects",
                  responses={
                         404: {
                             "model": Err,
                             "description": "Chat not found"
                         }
                     })
def chat_accounts(session: DBSession, chat_id: int) -> dict[str, dict[str, int] | list[DBAccount]]:
    chat = chats_db.get_by_id(session, chat_id)
    if chat is None:
        raise EntityNotFound("chat", chat_id)
    all_members = chats_db.get_chat_members(session, chat_id)
    metadata = len(all_members)
    return {"metadata": {"count": metadata}, "accounts": all_members}


@chats_router.post("/", response_model=Chat,
                   summary="Create a new chat",
                   response_description="Chat object",
                   status_code=201,
                   responses={
                       404: {
                           "model": Err,
                           "description": "Account not found"
                       },
                       422:{
                           "model": Err,
                           "description": "Chat name already exists"
                       }
                   })
def create_chat(chat: ChatCreate, session: DBSession) -> DBChat:
    return chats_db.create_chat(session, chat)


@chats_router.put("/{chat_id}", response_model=Chat, status_code=200)
def update_chat(chat: ChatUpdate, session: DBSession, chat_id: int) -> DBChat:
    return chats_db.update_chat(session, chat_id, chat)

@chats_router.delete("/{chat_id}", status_code=204)
def delete_chat(session: DBSession, chat_id: int):
    chats_db.delete_chat(session, chat_id)

@chats_router.post("/{chat_id}/messages", response_model=Message, status_code=201)
def add_message_to_chat(message: CreateMessage, chat_id: int, session: DBSession) -> DBMessage:
    return chats_db.add_chat_message(session, chat_id, message)

@chats_router.put("/{chat_id}/messages/{message_id}", response_model=Message, status_code=200)
def update_message_text(message: UpdateMessage, chat_id: int, message_id: int, session: DBSession) -> DBMessage:
    return chats_db.update_chat_message(session, chat_id, message_id, message)

@chats_router.delete("/{chat_id}/messages/{message_id}", status_code=204)
def delete_message_from_chat(chat_id: int, message_id: int, session: DBSession):
    chats_db.delete_chat_message(session, chat_id, message_id)

@chats_router.post("/{chat_id}/accounts", response_model=ChatMembership, status_code=201)
def add_account_to_chat(account: AddAccountToChat, chat_id: int, session: DBSession, response: Response = None):
    created, result = chats_db.add_account_to_chat(session, chat_id, account)
    response.status_code = 201 if created else 200
    return result

@chats_router.delete("/{chat_id}/accounts/{account_id}", status_code=204)
def delete_account_from_chat(chat_id: int, account_id: int, session: DBSession):
    chats_db.delete_account_from_chat(session, chat_id, account_id)