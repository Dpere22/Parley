import re

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
    assert "parley_token=" in cookies

def test_login_incorrect_password(setup_db, client, account_data, chat_data, message_data, chat_membership_data):
    data = {
        "username": "jamaron",
        "password": "test",
    }
    response = client.post("/auth/web/login", data=data)
    assert response.status_code == 401
    assert response.json() == {
        "error": "invalid_credentials",
        "message": "Authentication failed: invalid username or password"
    }



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

def test_logout_fail(setup_db, client, account_data, chat_data, message_data, chat_membership_data):
    response = client.post("/auth/web/logout")
    assert response.status_code == 403
    assert response.json() == {
        "error": "authentication_required",
        "message": "Not authenticated"
    }