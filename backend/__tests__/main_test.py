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

