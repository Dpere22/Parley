from fastapi import APIRouter
from typing import Annotated
chats_router = APIRouter(prefix="/chats", tags=["chats"])

#DBSession = Annotated[Session, Depends(get_session)]

@chats_router.get("/")
def chats():
    pass

@chats_router.get("/{chat_id}")
def get_chat(chat_id: int):
    pass

@chats_router.get("/{chat_id}/messages")
def messages(chat_id: int):
    pass

@chats_router.get("/chats/{chat_id}/accounts")
def chat_accounts(chat_id: int):
    pass
