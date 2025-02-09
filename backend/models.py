from datetime import datetime

from pydantic import BaseModel

from typing import Optional


class Metadata(BaseModel):
    count: int

class Account(BaseModel):
    id: int
    username: str

class Chat(BaseModel):
    id: int
    name: str
    owner_id: int
    
class Accounts(BaseModel):
    metadata: Metadata
    accounts: list[Account]

class Chats(BaseModel):
    metadata: Metadata
    chats: list[Chat]

class Message(BaseModel):
    id: int
    text: str
    account_id: int
    chat_id: int
    created_at: datetime

class ChatMessages(BaseModel):
    metadata: Metadata
    messages: list[Message]

class ChatAccounts(BaseModel):
    metadata: Metadata
    accounts: list[Account]

class ChatCreate(BaseModel):
    name: str
    owner_id: int

class ChatUpdate(BaseModel):
    name: Optional[str] = None
    owner_id: Optional[int] = None

class CreateMessage(BaseModel):
    text: str
    account_id: int

class UpdateMessage(BaseModel):
    text: str

class AddAccountToChat(BaseModel):
    account_id: int

class ChatMembership(BaseModel):
    chat_id: int
    account_id: int
