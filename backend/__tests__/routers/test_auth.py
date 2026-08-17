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

def test_login_hashes_even_for_unknown_username(setup_db, client, monkeypatch):
    """An unknown username must still cost a password comparison.

    Short-circuiting before bcrypt made login a timing oracle for which accounts
    exist - measured at roughly 190ms versus 2ms. Counting the calls is the
    deterministic way to assert this; timing the two paths would be flaky.
    """
    from backend.database import password as password_utils

    calls = []
    real_verify = password_utils.verify_password
    monkeypatch.setattr(
        password_utils,
        "verify_password",
        lambda pw, hashed: calls.append(1) or real_verify(pw, hashed),
    )

    known = client.post("/auth/token", data={"username": "loldleman", "password": "wrong"})
    assert known.status_code == 401
    assert len(calls) == 1

    unknown = client.post("/auth/token", data={"username": "nobody-at-all", "password": "wrong"})
    assert unknown.status_code == 401
    assert len(calls) == 2, "no password comparison was made for the unknown username"

    ## and the two are indistinguishable to the caller
    assert known.json() == unknown.json()


def test_registration_rejects_short_password(setup_db, client):
    response = client.post(
        "/auth/registration",
        data={"username": "newbie", "email": "newbie@example.com", "password": "short"},
    )
    assert response.status_code == 422


def test_registration_rejects_password_past_bcrypt_limit(setup_db, client):
    ## bcrypt ignores anything past 72 bytes, so accepting this would silently store a
    ## different password than the one the user typed
    response = client.post(
        "/auth/registration",
        data={"username": "newbie", "email": "newbie@example.com", "password": "a" * 73},
    )
    assert response.status_code == 422


def test_registration_rejects_malformed_email(setup_db, client):
    response = client.post(
        "/auth/registration",
        data={"username": "newbie", "email": "not-an-address", "password": "goodpassword"},
    )
    assert response.status_code == 422


def test_registration_is_case_insensitive_on_email(setup_db, client):
    ## jamaron already holds jm@jm.com
    response = client.post(
        "/auth/registration",
        data={"username": "newbie", "email": "JM@JM.COM", "password": "goodpassword"},
    )
    assert response.status_code == 422
    assert response.json()["error"] == "duplicate_entity_value"


def test_password_change_rejects_short_password(setup_db, client, authenticated_headers):
    response = client.put(
        "/accounts/me/password",
        headers=authenticated_headers,
        data={"old_password": "password", "new_password": "short"},
    )
    assert response.status_code == 422
