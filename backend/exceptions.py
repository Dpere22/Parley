from starlette.responses import JSONResponse, Response
from pydantic import BaseModel

class Err(BaseModel):
    error: str
    message: str

class EntityNotFound(Exception):
    def __init__(self, entity_name: str, entity_id: int):
        self.status_code = 404
        message = f"Unable to find {entity_name} with id={entity_id}"
        self.message = message

    def response(self) -> Response:
        return JSONResponse(
            status_code = self.status_code,
            content = Err(error = "entity_not_found", message = self.message).model_dump(),
        )

class DuplicateEntityValue(Exception):
    def __init__(self, entity_name: str):
        self.status_code = 422
        message = f"Duplicate value: chat with name={entity_name} already exists"
        self.message = message

    def response(self) -> Response:
        return JSONResponse(
            status_code = self.status_code,
            content=Err(error = "duplicate_entity_value", message = self.message).model_dump(),
        )

class AccountNotInChat(Exception):
    def __init__(self, account_id: int, chat_id: int):
        self.status_code = 422
        message = f"Account with id={account_id} must be a member of chat with id={chat_id}"
        self.message = message
    def response(self) -> Response:
        return JSONResponse(
            status_code = self.status_code,
            content=Err(error = "chat_membership_required", message = self.message).model_dump(),
        )

class OwnerRemoval(Exception):
    def __init__(self):
        self.status_code = 422
        message = f"Unable to remove the owner of a chat"
        self.message = message
    def response(self) -> Response:
        return JSONResponse(
            status_code = self.status_code,
            content=Err(error = "chat_owner_removal", message = self.message).model_dump(),
        )