def test_get_accounts(setup_db, client, account_data, chat_data):
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

def test_get_account_by_id(setup_db, client, account_data, chat_data):
    response = client.get("/accounts/1")
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "username": "jamaron"
    }

def test_get_chats(setup_db, client, account_data, chat_data):
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

