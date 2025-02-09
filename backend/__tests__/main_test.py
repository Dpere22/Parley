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
        "message": "Duplicate value: chat with name gamers already exists"
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
        "message": "Duplicate value: chat with name theboys already exists"
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