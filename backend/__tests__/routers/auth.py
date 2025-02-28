import re

def test_add_message_chat_does_not_exist(setup_db, client, account_data, chat_data, message_data, chat_membership_data):
    token_response = client.post("/auth/token", data={"username": "jamaron", "password": "password"})
    assert token_response.status_code == 200
    token = token_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    request_data = {
        "text": "testing",
        "account_id": 1
    }
    response = client.post("/chats/8/messages", json=request_data, headers = headers)
    assert response.status_code == 404
    assert response.json() == {
        "error": "entity_not_found",
        "message": "Unable to find chat with id=8"
    }

def test_registration(setup_db, client, account_data, chat_data, message_data, chat_membership_data):
    data = {
        "username": "TEST",
        "email": "TEST@TEST.com",
        "password": "password",
    }
    response = client.post("/auth/registration", data=data)
    assert response.status_code == 201

def test_token(setup_db, client, account_data, chat_data, message_data, chat_membership_data):
    data = {
        "username": "jamaron",
        "password": "password",
    }
    response = client.post("/auth/token", data=data)
    assert response.status_code == 200
    token = response.json()
    assert token["token_type"] == "bearer"
    jwt_pattern = r"^[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+$"
    assert re.match(jwt_pattern, token["access_token"])

def test_login(setup_db, client, account_data, chat_data, message_data, chat_membership_data):
    data = {
        "username": "jamaron",
        "password": "password",
    }
    response = client.post("/auth/web/login", data=data)
    assert response.status_code == 204
    cookies = response.headers["set-cookie"]
    assert "pony_express_token=" in cookies

def test_logout(setup_db, client, account_data, chat_data, message_data, chat_membership_data):
    data = {
        "username": "jamaron",
        "password": "password",
    }
    response = client.post("/auth/web/login", data=data)
    assert response.status_code == 204
    response2 = client.post("/auth/web/logout")
    assert response2.status_code == 204
    response3 = client.get("/accounts/me")
    assert response3.status_code == 403