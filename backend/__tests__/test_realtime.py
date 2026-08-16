import pytest
from starlette.websockets import WebSocketDisconnect


def _token(headers) -> str:
    return headers["Authorization"].removeprefix("Bearer ")


def test_socket_rejects_missing_token(setup_db, client):
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect("/chats/1/ws") as websocket:
            websocket.receive_json()
    assert exc_info.value.code == 4401


def test_socket_rejects_invalid_token(setup_db, client):
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect("/chats/1/ws?token=not-a-real-token") as websocket:
            websocket.receive_json()
    assert exc_info.value.code == 4401


def test_socket_rejects_non_member(setup_db, client, outsider_headers):
    ## john belongs to no chat
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect(f"/chats/1/ws?token={_token(outsider_headers)}") as websocket:
            websocket.receive_json()
    assert exc_info.value.code == 4403


def test_socket_receives_new_message(setup_db, client, authenticated_headers, jamaron_headers):
    ## loldleman watches chat 1 while jamaron posts to it
    with client.websocket_connect(f"/chats/1/ws?token={_token(authenticated_headers)}") as websocket:
        response = client.post(
            "/chats/1/messages",
            json={"text": "is this thing on", "account_id": 1},
            headers=jamaron_headers,
        )
        assert response.status_code == 201

        event = websocket.receive_json()
        assert event["type"] == "message_new"
        assert event["payload"]["text"] == "is this thing on"
        assert event["payload"]["chat_id"] == 1
        assert event["payload"]["account_id"] == 1
        ## the payload matches what GET /chats/1/messages would have returned
        assert event["payload"] == response.json()


def test_socket_receives_edited_message(setup_db, client, authenticated_headers, jamaron_headers):
    with client.websocket_connect(f"/chats/1/ws?token={_token(authenticated_headers)}") as websocket:
        response = client.put(
            "/chats/1/messages/1",
            json={"text": "edited in flight"},
            headers=jamaron_headers,
        )
        assert response.status_code == 200

        event = websocket.receive_json()
        assert event["type"] == "message_edit"
        assert event["payload"]["id"] == 1
        assert event["payload"]["text"] == "edited in flight"


def test_socket_receives_deleted_message(setup_db, client, authenticated_headers, jamaron_headers):
    with client.websocket_connect(f"/chats/1/ws?token={_token(authenticated_headers)}") as websocket:
        response = client.delete("/chats/1/messages/1", headers=jamaron_headers)
        assert response.status_code == 204

        event = websocket.receive_json()
        assert event["type"] == "message_delete"
        assert event["payload"] == {"id": 1, "chat_id": 1}


def test_socket_receives_member_join(setup_db, client, authenticated_headers, outsider_headers):
    with client.websocket_connect(f"/chats/1/ws?token={_token(authenticated_headers)}") as websocket:
        response = client.post(
            "/chats/1/accounts",
            json={"account_id": 3},
            headers=outsider_headers,
        )
        assert response.status_code == 201

        event = websocket.receive_json()
        assert event["type"] == "member_join"
        assert event["payload"] == {"chat_id": 1, "account_id": 3}


def test_socket_receives_member_leave(setup_db, client, jamaron_headers, authenticated_headers):
    ## jamaron owns chat 1 and watches it while loldleman leaves
    with client.websocket_connect(f"/chats/1/ws?token={_token(jamaron_headers)}") as websocket:
        response = client.delete("/chats/1/accounts/2", headers=authenticated_headers)
        assert response.status_code == 204

        event = websocket.receive_json()
        assert event["type"] == "member_leave"
        assert event["payload"] == {"chat_id": 1, "account_id": 2}


def test_events_do_not_leak_across_chats(setup_db, client, authenticated_headers):
    ## loldleman watches chat 2 while a message goes to chat 1, then to chat 2. If the
    ## chat 1 message leaked it would be the first frame read here.
    with client.websocket_connect(f"/chats/2/ws?token={_token(authenticated_headers)}") as websocket:
        response = client.post(
            "/chats/1/messages",
            json={"text": "different room", "account_id": 2},
            headers=authenticated_headers,
        )
        assert response.status_code == 201

        response = client.post(
            "/chats/2/messages",
            json={"text": "this room", "account_id": 2},
            headers=authenticated_headers,
        )
        assert response.status_code == 201

        event = websocket.receive_json()
        assert event["payload"]["text"] == "this room"


## The manager's bookkeeping is exercised directly: asserting on it through a live
## socket races the server task that registers the connection.

def test_manager_add_and_remove():
    from backend.realtime import ConnectionManager

    manager = ConnectionManager()
    socket = object()

    manager.add(1, socket)
    assert manager.connection_count(1) == 1

    manager.remove(1, socket)
    assert manager.connection_count(1) == 0

    ## removing twice, or removing from an unknown chat, is a no-op
    manager.remove(1, socket)
    manager.remove(99, socket)
    assert manager.connection_count(1) == 0


def test_broadcast_prunes_sockets_that_fail_to_send():
    import asyncio

    from backend.realtime import ConnectionManager

    class FakeSocket:
        def __init__(self, alive: bool):
            self.alive = alive
            self.sent: list[dict] = []

        async def send_json(self, event: dict) -> None:
            if not self.alive:
                raise RuntimeError("socket is closed")
            self.sent.append(event)

    manager = ConnectionManager()
    alive, dead = FakeSocket(True), FakeSocket(False)
    manager.add(1, alive)
    manager.add(1, dead)

    asyncio.run(manager.broadcast(1, {"type": "message_new"}))

    assert alive.sent == [{"type": "message_new"}]
    assert manager.connection_count(1) == 1
