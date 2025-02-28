from datetime import datetime, timezone
from jose import jwt

def test_invalid_token(setup_db, client, account_data, message_data, chat_membership_data):
    iat = int(datetime.now(timezone.utc).timestamp())
    exp = iat + 3600
    token = jwt.encode(
        {"sub": "1", "iss": "http://127.0.0.1", "iat": iat, "exp": exp},
        "invalid-jwt-secret-key",
    )
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/accounts/me", headers=headers)
    assert response.status_code == 403
    assert response.json() == {"error": "invalid_access_token", "message": "Authentication failed: invalid access token"}

