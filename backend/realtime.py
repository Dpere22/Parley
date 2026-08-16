"""Fan-out of chat events to connected WebSocket clients.

Event payloads reuse the pydantic models the REST endpoints return, so a client can
write a broadcast straight into the cache it filled from the matching GET.

State lives in a module level `manager`, which means it is per-process. Running more
than one worker needs a shared broker (Redis pub/sub or similar) behind this same
interface.
"""

from fastapi import WebSocket

from backend.database.schema import DBMessage
from backend.models import Message

MESSAGE_NEW = "message_new"
MESSAGE_EDIT = "message_edit"
MESSAGE_DELETE = "message_delete"
MEMBER_JOIN = "member_join"
MEMBER_LEAVE = "member_leave"


class ConnectionManager:
    """Tracks the open sockets watching each chat."""

    def __init__(self) -> None:
        self._rooms: dict[int, set[WebSocket]] = {}

    def add(self, chat_id: int, websocket: WebSocket) -> None:
        self._rooms.setdefault(chat_id, set()).add(websocket)

    def remove(self, chat_id: int, websocket: WebSocket) -> None:
        room = self._rooms.get(chat_id)
        if room is None:
            return
        room.discard(websocket)
        if not room:
            del self._rooms[chat_id]

    def connection_count(self, chat_id: int) -> int:
        return len(self._rooms.get(chat_id, ()))

    async def broadcast(self, chat_id: int, event: dict) -> None:
        room = self._rooms.get(chat_id)
        if not room:
            return
        # A send can fail on a socket the client already dropped. Collect those and
        # prune them afterwards rather than mutating the room mid-iteration.
        broken: list[WebSocket] = []
        for websocket in list(room):
            try:
                await websocket.send_json(event)
            except Exception:
                broken.append(websocket)
        for websocket in broken:
            self.remove(chat_id, websocket)


manager = ConnectionManager()


def message_event(event_type: str, message: DBMessage) -> dict:
    return {
        "type": event_type,
        "payload": Message(**message.model_dump()).model_dump(mode="json"),
    }


def message_deleted_event(chat_id: int, message_id: int) -> dict:
    return {
        "type": MESSAGE_DELETE,
        "payload": {"id": message_id, "chat_id": chat_id},
    }


def membership_event(event_type: str, chat_id: int, account_id: int) -> dict:
    return {
        "type": event_type,
        "payload": {"chat_id": chat_id, "account_id": account_id},
    }
