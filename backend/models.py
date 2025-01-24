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