from starlette.responses import JSONResponse, Response
from pydantic import BaseModel

class NotFound(BaseModel):
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
            content = NotFound(error = "entity_not_found", message = self.message).model_dump(),
        )

class DuplicateEntity(BaseModel):
    error: str
    message: str

class DuplicateEntityValue(Exception):
    def __init__(self, entity_name: str):
        self.status_code = 422
        message = f"Duplicate value: chat with name {entity_name} already exists"
        self.message = message

    def response(self) -> Response:
        return JSONResponse(
            status_code = self.status_code,
            content=DuplicateEntity(error = "duplicate_entity_value", message = self.message).model_dump(),
        )
