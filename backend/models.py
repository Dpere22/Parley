from datetime import datetime

from pydantic import BaseModel

from typing import Optional


class Metadata(BaseModel):
    count: int

class Account(BaseModel):
    id: int
    username: str

class User(BaseModel):
    id: int
    username: str
    email: str

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
    account_id: Optional[int] = None
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

class Registration(BaseModel):
    username: str
    email: str
    password: str

class Login(BaseModel):
    username: str
    password: str

class AccessToken(BaseModel):
    access_token: str
    token_type: str

class Claims(BaseModel):
    sub: str
    iss: str
    iat: int
    exp: int

class AccountUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None

class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str
