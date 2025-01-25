from backend.database.schema import DBAccount

def test_get_accounts(session, client):
    session.add(DBAccount(username="jamaron", hashed_password="123", email="jm@jm.com", id = 1))
    session.commit()
    response = client.get("/accounts")
    assert response.status_code == 200
    assert response.json() == {
        "metadata": {"count": 1},
        "accounts": [
            {
                "id": 1,
                "username": "jamaron"
            }
        ]
    }

