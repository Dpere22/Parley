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

def test_get_accounts_me_with_token_status_code(setup_db, client, account_data, message_data, chat_membership_data, authenticated_headers):
    response = client.get("/accounts/me", headers=authenticated_headers)
    assert response.status_code == 200

def test_update_me_status_username(setup_db, client, account_data, message_data, chat_membership_data, authenticated_headers):
    request_data = {
        "username": "UPDATED"
    }
    response = client.put("/accounts/me", headers=authenticated_headers, json=request_data)
    assert response.status_code == 200

def test_update_me_status_email(setup_db, client, account_data, message_data, chat_membership_data, authenticated_headers):
    request_data = {
        "email": "updated@example.com"
    }
    response = client.put("/accounts/me", headers=authenticated_headers, json=request_data)
    assert response.status_code == 200
    assert response.json()["email"] == "updated@example.com"

def test_update_me_rejects_malformed_email(setup_db, client, authenticated_headers):
    response = client.put("/accounts/me", headers=authenticated_headers, json={"email": "not-an-address"})
    assert response.status_code == 422

def test_update_me_email_is_lowercased(setup_db, client, authenticated_headers):
    response = client.put("/accounts/me", headers=authenticated_headers, json={"email": "MiXeD@Example.COM"})
    assert response.status_code == 200
    assert response.json()["email"] == "mixed@example.com"

def test_update_me_username(setup_db, client, account_data, message_data, chat_membership_data, authenticated_headers):
    request_data = {
        "username": "UPDATED"
    }
    response = client.put("/accounts/me", headers=authenticated_headers, json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "UPDATED"

def test_update_me_password(setup_db, client, account_data, message_data, chat_membership_data, authenticated_headers):
    response1 = client.put("/accounts/me/password", headers=authenticated_headers, data={"old_password": "password", "new_password": "new_password"})
    assert response1.status_code == 204
    response2 = client.post("/auth/token", data={"username": "loldleman", "password": "new_password"})
    assert response2.status_code == 200

def test_update_me_password_wrong_old_password(setup_db, client, account_data, message_data, chat_membership_data, authenticated_headers):
    response = client.put("/accounts/me/password", headers=authenticated_headers, data={"old_password": "wrong_password", "new_password": "new_password"})
    assert response.status_code == 401


def test_remove_me_own_chats(setup_db, client, account_data, message_data, chat_membership_data, authenticated_headers):
    response = client.delete("/accounts/me", headers=authenticated_headers)
    assert response.status_code == 422

def test_remove_me(setup_db, client, account_data, message_data, chat_membership_data):
    token_response = client.post("/auth/token", data={"username": "john", "password": "password"})
    assert token_response.status_code == 200
    token = token_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.delete("/accounts/me", headers=headers)
    assert response.status_code == 204

def test_get_my_chats(setup_db, client, authenticated_headers):
    ## loldleman belongs to both chats
    response = client.get("/accounts/me/chats", headers=authenticated_headers)
    assert response.status_code == 200
    assert response.json() == {
        "metadata": {"count": 2},
        "chats": [
            {"id": 1, "name": "gamers", "owner_id": 1},
            {"id": 2, "name": "theboys", "owner_id": 2},
        ]
    }

def test_get_my_chats_excludes_chats_not_joined(setup_db, client, jamaron_headers):
    ## jamaron belongs only to chat 1, while GET /chats returns both
    response = client.get("/accounts/me/chats", headers=jamaron_headers)
    assert response.status_code == 200
    assert response.json() == {
        "metadata": {"count": 1},
        "chats": [{"id": 1, "name": "gamers", "owner_id": 1}]
    }
    assert client.get("/chats").json()["metadata"] == {"count": 2}

def test_get_my_chats_when_member_of_none(setup_db, client, outsider_headers):
    response = client.get("/accounts/me/chats", headers=outsider_headers)
    assert response.status_code == 200
    assert response.json() == {"metadata": {"count": 0}, "chats": []}

def test_get_my_chats_not_authenticated(setup_db, client):
    response = client.get("/accounts/me/chats")
    assert response.status_code == 403
