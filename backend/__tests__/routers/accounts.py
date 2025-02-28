def test_get_accounts(setup_db, client, account_data, chat_data,  message_data, chat_membership_data):
    response = client.get("/accounts")
    assert response.status_code == 200
    assert response.json() == {
        "metadata": {"count": 3},
        "accounts": [
            {
                "id": 1,
                "username": "jamaron"
            },
            {
                "id": 2,
                "username": "loldleman"
            },
            {
                "id": 3,
                "username": "john"
            }
        ]
    }

def test_get_account_by_id(setup_db, client, account_data, chat_data,  message_data, chat_membership_data):
    response = client.get("/accounts/1")
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "username": "jamaron"
    }

def test_get_account_by_id_fail(setup_db, client, account_data, chat_data, message_data, chat_membership_data):
    response = client.get("/accounts/4")
    assert response.status_code == 404
    assert response.json() == {
        "error": "entity_not_found",
        "message": "Unable to find account with id=4"
    }

def test_get_accounts_me_with_token_status_code(setup_db, client, account_data, message_data, chat_membership_data):
    token_response = client.post("/auth/token", data={"username": "loldleman", "password": "password"})
    assert token_response.status_code == 200
    token = token_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/accounts/me", headers=headers)
    assert response.status_code == 200

def test_update_me_status_username(setup_db, client, account_data, message_data, chat_membership_data):
    token_response = client.post("/auth/token", data={"username": "loldleman", "password": "password"})
    assert token_response.status_code == 200
    token = token_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    request_data = {
        "username": "UPDATED"
    }
    response = client.put("/accounts/me", headers=headers, json=request_data)
    assert response.status_code == 200

def test_update_me_status_email(setup_db, client, account_data, message_data, chat_membership_data):
    token_response = client.post("/auth/token", data={"username": "loldleman", "password": "password"})
    assert token_response.status_code == 200
    token = token_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    request_data = {
        "email": "UPDATED"
    }
    response = client.put("/accounts/me", headers=headers, json=request_data)
    assert response.status_code == 200

def test_update_me_username(setup_db, client, account_data, message_data, chat_membership_data):
    token_response = client.post("/auth/token", data={"username": "loldleman", "password": "password"})
    assert token_response.status_code == 200
    token = token_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    request_data = {
        "username": "UPDATED"
    }
    response = client.put("/accounts/me", headers=headers, json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "UPDATED"

def test_update_password_persist(setup_db, client, account_data, message_data, chat_membership_data):
    token_response = client.post("/auth/token", data={"username": "loldleman", "password": "password"})
    assert token_response.status_code == 200
    token = token_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response1 = client.put("/accounts/me/password", headers=headers, data={"old_password": "password", "new_password": "new_password"})
    assert response1.status_code == 204
    response2 = client.post("/auth/token", data={"username": "loldleman", "password": "new_password"})
    assert response2.status_code == 200

def test_update_password_wrong_old_password(setup_db, client, account_data, message_data, chat_membership_data):
    token_response = client.post("/auth/token", data={"username": "loldleman", "password": "password"})
    assert token_response.status_code == 200
    token = token_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response1 = client.put("/accounts/me/password", headers=headers, data={"old_password": "wrong_password", "new_password": "new_password"})
    assert response1.status_code == 401


def test_remove_login_account_own_chats(setup_db, client, account_data, message_data, chat_membership_data):
    token_response = client.post("/auth/token", data={"username": "loldleman", "password": "password"})
    assert token_response.status_code == 200
    token = token_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.delete("/accounts/me", headers=headers)
    assert response.status_code == 422

def test_remove_login_account(setup_db, client, account_data, message_data, chat_membership_data):
    token_response = client.post("/auth/token", data={"username": "john", "password": "password"})
    assert token_response.status_code == 200
    token = token_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.delete("/accounts/me", headers=headers)
    assert response.status_code == 204