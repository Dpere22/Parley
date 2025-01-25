from datetime import datetime

from pydantic import BaseModel

class Account(BaseModel):
    id: int
    username: str

class Chat(BaseModel):
    id: int
    name: str
    owner_id: int

class Accounts(BaseModel):
    metadata: int
    accounts: list[Account]

class Chats(BaseModel):
    metadata: int
    chats: list[Chat]

class Message(BaseModel):
    id: int
    text: str
    account_id: int
    chat_id: int
    created_at: datetime

class ChatMessages(BaseModel):
    metadata: int
    messages: list[Message]

class ChatMembers(BaseModel):
    metadata: int
    members: list[Account]