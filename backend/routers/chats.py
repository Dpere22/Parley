from typing import Annotated

from fastapi import APIRouter, Response, Depends, Query, WebSocket, WebSocketDisconnect

from backend.database import chats as chats_db
from backend.database.auth import get_current_user, extract_user
from backend.database.schema import DBChat, DBMessage, DBAccount
from backend.dependencies import DBSession
from backend.exceptions import EntityNotFound, Err
from backend.models import *
from backend.realtime import (
    MEMBER_JOIN,
    MEMBER_LEAVE,
    MESSAGE_EDIT,
    MESSAGE_NEW,
    manager,
    membership_event,
    message_deleted_event,
    message_event,
)

chats_router = APIRouter(prefix="/chats", tags=["chats"])

## close codes for the chat socket, in the private 4000-4999 range
WS_UNAUTHENTICATED = 4401
WS_NOT_A_MEMBER = 4403


@chats_router.websocket("/{chat_id}/ws")
async def chat_socket(websocket: WebSocket, chat_id: int, session: DBSession, token: str | None = Query(default=None)):
    """Stream chat events to a member of the chat.

    A browser cannot set headers on a WebSocket handshake, so the access token arrives
    as a query parameter and is validated with the same helper the HTTP routes use.
    """
    await websocket.accept()

    if token is None:
        await websocket.close(code=WS_UNAUTHENTICATED)
        return
    try:
        user = extract_user(session, token)
    except Exception:
        await websocket.close(code=WS_UNAUTHENTICATED)
        return

    members = chats_db.get_chat_members(session, chat_id)
    if user.id not in {member.id for member in members}:
        await websocket.close(code=WS_NOT_A_MEMBER)
        return

    manager.add(chat_id, websocket)
    try:
        ## the client never sends commands, so this just parks until it goes away
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.remove(chat_id, websocket)
    except Exception:
        manager.remove(chat_id, websocket)


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
                       },
                       403:{
                           "model": Err,
                           "description": "User not authenticated, please log in"
                       }
                   })
def create_chat(chat: ChatCreate, session: DBSession, user: Annotated[DBAccount, Depends(get_current_user)]) -> DBChat:
    return chats_db.create_chat(session, chat, user)


@chats_router.put("/{chat_id}",
                  response_model=Chat,
                  summary="Update either a chat name or chat owner",
                  response_description="Chat object",
                  status_code=200,
                  responses={
                      404: {
                          "model": Err,
                          "description": "Chat not found"
                      },
                      422: {
                          "model": Err,
                          "description": "Chat name already exists or account not in chat or account doesn't exist"
                      },
                      403: {
                          "model": Err,
                          "description": "Not authenticated, or not the owner of the chat"
                      }
                  })
def update_chat(chat: ChatUpdate, session: DBSession, chat_id: int, user: Annotated[DBAccount, Depends(get_current_user)]) -> DBChat:
    return chats_db.update_chat(session, chat_id, chat, user)

@chats_router.delete("/{chat_id}",
                     status_code=204,
                     summary="Delete a chat by id",
                     responses={
                         404: {
                             "model": Err,
                             "description": "Chat not found"
                         },
                         403: {
                             "model": Err,
                             "description": "Not authenticated, or not the owner of the chat"
                         }
                     })
def delete_chat(session: DBSession, chat_id: int, user: Annotated[DBAccount, Depends(get_current_user)]):
    chats_db.delete_chat(session, chat_id, user)

@chats_router.post("/{chat_id}/messages",
                   response_model=Message,
                   summary="Add a message to the chat",
                   status_code=201,
                   response_description="Created Message object",
                   responses={
                       404: {
                           "model": Err,
                           "description": "Chat not found"
                       },
                       422: {
                           "model": Err,
                           "description": "Account does not exist or isn't a part of the chat"
                       },
                       403: {
                           "model": Err,
                           "description": "User not authenticated, please log in or cannot chat on behalf of another account"
                       }
                   })
async def add_message_to_chat(message: CreateMessage, chat_id: int, session: DBSession, user: Annotated[DBAccount, Depends(get_current_user)]) -> DBMessage:
    db_message = chats_db.add_chat_message(session, chat_id, message, user)
    await manager.broadcast(chat_id, message_event(MESSAGE_NEW, db_message))
    return db_message

@chats_router.put("/{chat_id}/messages/{message_id}",
                  response_model=Message,
                  summary="Update a message's text in the chat",
                  response_description="Updated Message object",
                  status_code=200,
                  responses={
                      404: {
                          "model": Err,
                          "description": "Chat not found or the message doesn't exist"
                      },
                      403: {
                          "model": Err,
                          "description": "Not authenticated, or not the author of the message"
                      }
                  })
async def update_message_text(message: UpdateMessage, chat_id: int, message_id: int, session: DBSession, user: Annotated[DBAccount, Depends(get_current_user)]) -> DBMessage:
    db_message = chats_db.update_chat_message(session, chat_id, message_id, message, user)
    await manager.broadcast(chat_id, message_event(MESSAGE_EDIT, db_message))
    return db_message

@chats_router.delete("/{chat_id}/messages/{message_id}",
                     status_code=204,
                     summary="Delete a message in a chat",
                     responses={
                         404: {
                             "model": Err,
                             "description": "Chat not found or the message doesn't exist"
                         },
                         403: {
                             "model": Err,
                             "description": "Not authenticated, or not the author of the message nor the chat owner"
                         }
                     })
async def delete_message_from_chat(chat_id: int, message_id: int, session: DBSession, user: Annotated[DBAccount, Depends(get_current_user)]):
    chats_db.delete_chat_message(session, chat_id, message_id, user)
    await manager.broadcast(chat_id, message_deleted_event(chat_id, message_id))

@chats_router.post("/{chat_id}/accounts",
                   response_model=ChatMembership,
                   summary="Add an account to a chat",
                   response_description="Account membership",
                   status_code=201,
                   responses={
                       200: {
                           "description": "Account already in chat"
                       },
                       404:{
                           "model": Err,
                           "description": "Chat not found or account not found"
                       },
                       403: {
                           "model": Err,
                           "description": "Not authenticated, or adding another account without owning the chat"
                       }
                   })
async def add_account_to_chat(account: AddAccountToChat, chat_id: int, session: DBSession, user: Annotated[DBAccount, Depends(get_current_user)], response: Response = None):
    created, result = chats_db.add_account_to_chat(session, chat_id, account, user)
    response.status_code = 201 if created else 200
    if created:
        await manager.broadcast(chat_id, membership_event(MEMBER_JOIN, chat_id, account.account_id))
    return result

@chats_router.delete("/{chat_id}/accounts/{account_id}",
                     status_code=204,
                     summary="Delete an account from a chat",
                     responses={
                         404: {
                             "model": Err,
                             "description": "Chat not found"
                         },
                         422: {
                             "model": Err,
                             "description": "Account does not exist or isn't a part of the chat or is the owner of the chat"
                         },
                         403: {
                             "model": Err,
                             "description": "Not authenticated, or removing another account without owning the chat"
                         }
                     })
async def delete_account_from_chat(chat_id: int, account_id: int, session: DBSession, user: Annotated[DBAccount, Depends(get_current_user)]):
    chats_db.delete_account_from_chat(session, chat_id, account_id, user)
    await manager.broadcast(chat_id, membership_event(MEMBER_LEAVE, chat_id, account_id))