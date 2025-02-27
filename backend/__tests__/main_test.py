def test_get_accounts(setup_db, client, account_data, chat_data,  message_data, chat_membership_data):
    response = client.get("/accounts")
    assert response.status_code == 200
    assert response.json() == {
        "metadata": {"count": 2},
        "accounts": [
            {
                "id": 1,
                "username": "jamaron"
            },
            {
                "id": 2,
                "username": "loldleman"
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
    response = client.get("/accounts/3")
    assert response.status_code == 404
    assert response.json() == {
        "error": "entity_not_found",
        "message": "Unable to find account with id=3"
    }

def test_get_all_chats(setup_db, client, account_data, chat_data,  message_data, chat_membership_data):
    response = client.get("/chats")
    assert response.status_code == 200
    assert response.json() == {
        "metadata": {"count": 2},
        "chats": [
            {
                "id": 1,
                "name": "gamers",
                "owner_id": 1
            },
            {
                "id": 2,
                "name": "theboys",
                "owner_id": 2
            }
        ]
    }

def test_get_chat_by_chat_id(setup_db, client, account_data, chat_data,  message_data, chat_membership_data):
    response = client.get("/chats/1")
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "name": "gamers",
        "owner_id": 1
    }

def test_get_chat_by_id_fail(setup_db, client, account_data, chat_data, message_data, chat_membership_data):
    response = client.get("/chats/3")
    assert response.status_code == 404
    assert response.json() == {
        "error": "entity_not_found",
        "message": "Unable to find chat with id=3"
    }


def test_get_chat_messages_by_chat_id(setup_db, client, account_data, chat_data, message_data, chat_membership_data):
    response = client.get("/chats/1/messages")
    assert response.status_code == 200
    assert response.json() == {
        "metadata": {"count": 2},
        "messages": [
            {
                "id": 1,
                "text": "hi gamers",
                "account_id": 1,
                "chat_id": 1,
                "created_at": "2025-01-25T05:19:49"
            },
            {
                "id": 2,
                "text": "hi :3",
                "account_id": 2,
                "chat_id": 1,
                "created_at": "2025-01-25T05:20:34"
            }
        ]
    }

def test_get_chat_messages_by_id_fail(setup_db, client, account_data, chat_data, message_data, chat_membership_data):
    response = client.get("/chats/3/messages")
    assert response.status_code == 404
    assert response.json() == {
        "error": "entity_not_found",
        "message": "Unable to find chat with id=3"
    }

def test_get_chat_accounts_by_chat_id(setup_db, client, account_data, chat_data, message_data, chat_membership_data):
    response = client.get("/chats/1/accounts")
    assert response.status_code == 200
    assert response.json() == {
        "metadata": {"count": 2},
        "accounts": [
            {
                "id": 1,
                "username": "jamaron"
            },
            {
                "id": 2,
                "username": "loldleman"
            }
        ]
    }

def test_get_chat_accounts_by_id_fail(setup_db, client, account_data, chat_data, message_data, chat_membership_data):
    response = client.get("/chats/3/accounts")
    assert response.status_code == 404
    assert response.json() == {
        "error": "entity_not_found",
        "message": "Unable to find chat with id=3"
    }

def test_create_chat(setup_db, client, account_data, chat_data, message_data, chat_membership_data):
    request_data = {
        "name": "gamers3",
        "owner_id": 1,
    }
    response = client.post("/chats", json=request_data)
    assert response.status_code == 201
    assert response.json() == {
        "id": 3,
        "name": "gamers3",
        "owner_id": 1
    }

def test_create_chat_account_fail(setup_db, client, account_data, chat_data, message_data, chat_membership_data):
    request_data = {
        "name": "gamers3",
        "owner_id": 14,
    }
    response = client.post("/chats", json=request_data)
    assert response.status_code == 404
    assert response.json() == {
        "error": "entity_not_found",
        "message": "Unable to find account with id=14"
    }

def test_create_chat_duplicate_name_fail(setup_db, client, account_data, chat_data, message_data, chat_membership_data):
    request_data = {
        "name": "gamers",
        "owner_id": 1,
    }
    response = client.post("/chats", json=request_data)
    assert response.status_code == 422
    assert response.json() == {
        "error": "duplicate_entity_value",
        "message": "Duplicate value: chat with name=gamers already exists"
    }

def test_update_chat_name(setup_db, client, account_data, chat_data, message_data, chat_membership_data):
    request_data = {
        "name": "reformed_gamers",
    }
    response = client.put("/chats/1", json=request_data)
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "name": "reformed_gamers",
        "owner_id": 1
    }

def test_update_chat_owner(setup_db, client, account_data, chat_data, message_data, chat_membership_data):
    request_data = {
        "owner_id": 2,
    }
    response = client.put("/chats/1", json=request_data)
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "name": "gamers",
        "owner_id": 2
    }

def test_update_chat_name_fail(setup_db, client, account_data, chat_data, message_data, chat_membership_data):
    request_data = {
        "name":"theboys"
    }
    response = client.put("/chats/1", json=request_data)
    assert response.status_code == 422
    assert response.json() == {
        "error": "duplicate_entity_value",
        "message": "Duplicate value: chat with name=theboys already exists"
    }

def test_update_chat_owner_fail(setup_db, client, account_data, chat_membership_data):
    request_data = {
        "owner_id": 1,
    }
    response = client.put("/chats/2", json=request_data)
    assert response.status_code == 422
    assert response.json() == {
        "error": "chat_membership_required",
        "message": "Account with id=1 must be a member of chat with id=2"
    }

def test_update_chat_does_not_exist_fail(setup_db, client, account_data, chat_membership_data):
    request_data = {
        "owner_id": 1,
    }
    response = client.put("/chats/7", json=request_data)
    assert response.status_code == 404
    assert response.json() == {
        "error": "entity_not_found",
        "message": "Unable to find chat with id=7"
    }

def test_delete_chat(setup_db, client, account_data, chat_data, message_data, chat_membership_data):
    response = client.delete("/chats/1")
    assert response.status_code == 204
    response2 = client.get("/chats/1")
    assert response2.status_code == 404

def test_delete_chat_does_not_exist_fail(setup_db, client, account_data, chat_data, message_data, chat_membership_data):
    response = client.delete("/chats/7")
    assert response.status_code == 404
    assert response.json() == {
        "error": "entity_not_found",
        "message": "Unable to find chat with id=7"
    }

def test_add_message_to_chat(setup_db, client, account_data, chat_data, message_data, chat_membership_data):
    request_data = {
        "text": "LoL kinda fun ngl",
        "account_id": 1
    }
    response = client.post("/chats/1/messages", json=request_data)
    assert response.status_code == 201
    server_response = response.json()
    assert server_response["id"] == 4
    assert server_response["text"] == "LoL kinda fun ngl"
    assert server_response["account_id"] == 1
    assert server_response["chat_id"] == 1

def test_add_message_chat_does_not_exist(setup_db, client, account_data, chat_data, message_data, chat_membership_data):
    request_data = {
        "text": "testing",
        "account_id": 1
    }
    response = client.post("/chats/8/messages", json=request_data)
    assert response.status_code == 404
    assert response.json() == {
        "error": "entity_not_found",
        "message": "Unable to find chat with id=8"
    }

def test_add_message_account_not_part_of_chat(setup_db, client, account_data, message_data, chat_membership_data):
    request_data = {
        "text": "testing",
        "account_id": 1
    }
    response = client.post("/chats/2/messages", json=request_data)
    assert response.status_code == 422
    assert response.json() == {
        "error": "chat_membership_required",
        "message": "Account with id=1 must be a member of chat with id=2"
    }

def test_update_message_text(setup_db, client, account_data, message_data, chat_membership_data):
    request_data = {
        "text": "hi imaginary friends!",
    }
    response = client.put("/chats/2/messages/3", json=request_data)
    assert response.status_code == 200
    server_response = response.json()
    assert server_response["id"] == 3
    assert server_response["text"] == "hi imaginary friends!"
    assert server_response["account_id"] == 2
    assert server_response["chat_id"] == 2

def test_update_message_chat_does_not_exist(setup_db, client, account_data, message_data, chat_membership_data):
    request_data = {
        "text": "testing",
    }
    response = client.put("/chats/4/messages/1", json=request_data)
    assert response.status_code == 404
    assert response.json() == {
        "error": "entity_not_found",
        "message": "Unable to find chat with id=4"
    }

def test_update_message_not_in_chat(setup_db, client, account_data, message_data, chat_membership_data):
    request_data = {
        "text": "testing",
    }
    response = client.put("/chats/2/messages/1", json=request_data)
    assert response.status_code == 404
    assert response.json() == {
        "error": "entity_not_found",
        "message": "Unable to find message with id=1"
    }

def test_delete_message(setup_db, client, account_data, message_data, chat_membership_data):
    response = client.delete("/chats/1/messages/1")
    assert response.status_code == 204

def test_delete_message_chat_does_not_exist(setup_db, client, account_data, message_data, chat_membership_data):
    response = client.delete("/chats/3/messages/1")
    assert response.status_code == 404
    assert response.json() == {
        "error": "entity_not_found",
        "message": "Unable to find chat with id=3"
    }

def test_delete_message_not_in_chat(setup_db, client, account_data, message_data, chat_membership_data):
    response = client.delete("/chats/1/messages/10")
    assert response.status_code == 404
    assert response.json() == {
        "error": "entity_not_found",
        "message": "Unable to find message with id=10"
    }

def test_add_account_to_chat(setup_db, client, account_data, message_data, chat_membership_data):
    request_data = {
        "account_id": 1
    }
    response = client.post("/chats/2/accounts", json=request_data)
    assert response.status_code == 201
    assert response.json() == {
        "chat_id": 2,
        "account_id": 1
    }
    response2 = client.get("/chats/2/accounts")
    assert response2.status_code == 200
    assert response2.json() == {
        "metadata": {"count": 2},
        "accounts": [
            {
                "id": 2,
                "username": "loldleman"
            },
            {
                "id": 1,
                "username": "jamaron"
            }
        ]
    }

def test_add_account_already_in_chat(setup_db, client, account_data, message_data, chat_membership_data):
    request_data = {
        "account_id": 1
    }
    response = client.post("/chats/1/accounts", json=request_data)
    assert response.status_code == 200

def test_add_account_chat_does_not_exist(setup_db, client, account_data, message_data, chat_membership_data):
    request_data = {
        "account_id": 1
    }
    response = client.post("/chats/4/accounts", json=request_data)
    assert response.status_code == 404
    assert response.json() == {
        "error": "entity_not_found",
        "message": "Unable to find chat with id=4"
    }
def test_add_nonexistent_account_to_chat(setup_db, client, account_data, message_data, chat_membership_data):
    request_data = {
        "account_id": 8
    }
    response = client.post("/chats/1/accounts", json=request_data)
    assert response.status_code == 404
    assert response.json() == {
        "error": "entity_not_found",
        "message": "Unable to find account with id=8"
    }

def test_remove_account_from_chat(setup_db, client, account_data, message_data, chat_membership_data):
    response = client.delete("/chats/1/accounts/2")
    assert response.status_code == 204
    response2 = client.get("/chats/1/messages")
    assert response2.status_code == 200
    assert response2.json() == {
        "metadata": {"count": 2},
        "messages": [
            {
                "id": 1,
                "text": "hi gamers",
                "account_id": 1,
                "chat_id": 1,
                "created_at": "2025-01-25T05:19:49"
            },
            {
                "id": 2,
                "text": "hi :3",
                "account_id": None,
                "chat_id": 1,
                "created_at": "2025-01-25T05:20:34"
            }
        ]
    }

def test_remove_account_owner_of_chat_fail(setup_db, client, account_data, message_data, chat_membership_data):
    response = client.delete("/chats/1/accounts/1")
    assert response.status_code == 422
    assert response.json() == {
        "error": "chat_owner_removal",
        "message": "Unable to remove the owner of a chat"
    }

def test_remove_account_not_in_chat_fail(setup_db, client, account_data, message_data, chat_membership_data):
    response = client.delete("/chats/2/accounts/1")
    assert response.status_code == 422
    assert response.json() == {
        "error": "chat_membership_required",
        "message": "Account with id=1 must be a member of chat with id=2"
    }

def test_remove_account_chat_does_not_exist(setup_db, client, account_data, message_data, chat_membership_data):
    response = client.delete("/chats/4/accounts/1")
    assert response.status_code == 404
    assert response.json() == {
        "error": "entity_not_found",
        "message": "Unable to find chat with id=4"
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