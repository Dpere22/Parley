from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from typing import Annotated, Optional


def _lowercase(value: Optional[str]) -> Optional[str]:
    """Fold an address to lower case so Bob@x.com and bob@x.com are one account."""
    return value if value is None else value.lower()


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

## bcrypt silently ignores anything past 72 bytes, so a longer password is not the
## password the user thinks it is. Reject rather than truncate.
Password = Annotated[str, Field(min_length=8, max_length=72)]


class Registration(BaseModel):
    username: str
    email: EmailStr
    password: Password

    _normalize_email = field_validator("email")(_lowercase)


## Deliberately unconstrained: the rules belong on registration and password change.
## Applying them here would lock out any account whose password predates them, and
## would advertise the policy to anyone probing the login endpoint.
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
    email: Optional[EmailStr] = None

    _normalize_email = field_validator("email")(_lowercase)

class PasswordUpdate(BaseModel):
    ## the old password is only compared, never stored, so it carries no rules
    old_password: str
    new_password: Password
