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



def _token(claims: dict, key: str | None = None) -> str:
    from backend.settings import settings
    return jwt.encode(claims, key or settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def _claims(**overrides) -> dict:
    from backend.settings import settings
    iat = int(datetime.now(timezone.utc).timestamp())
    base = {"sub": "1", "iss": settings.jwt_issuer, "iat": iat, "exp": iat + 3600}
    base.update(overrides)
    return base


def test_expired_token(setup_db, client):
    ## signed with the real key, but issued and expired in the past
    iat = int(datetime.now(timezone.utc).timestamp()) - 7200
    headers = {"Authorization": f"Bearer {_token(_claims(iat=iat, exp=iat + 3600))}"}
    response = client.get("/accounts/me", headers=headers)
    assert response.status_code == 403
    assert response.json() == {
        "error": "expired_access_token",
        "message": "Authentication failed: expired access token",
    }


def test_token_with_wrong_issuer(setup_db, client):
    headers = {"Authorization": f"Bearer {_token(_claims(iss='http://evil.example'))}"}
    response = client.get("/accounts/me", headers=headers)
    assert response.status_code == 403
    assert response.json()["error"] == "invalid_access_token"


def test_token_with_missing_claim(setup_db, client):
    ## validly signed, but the payload does not satisfy the Claims model. This must be
    ## a 403 rather than a 500, which is what a too-narrow except clause would give.
    claims = _claims()
    del claims["iat"]
    headers = {"Authorization": f"Bearer {_token(claims)}"}
    response = client.get("/accounts/me", headers=headers)
    assert response.status_code == 403
    assert response.json()["error"] == "invalid_access_token"


def test_token_with_non_numeric_subject(setup_db, client):
    headers = {"Authorization": f"Bearer {_token(_claims(sub='not-a-number'))}"}
    response = client.get("/accounts/me", headers=headers)
    assert response.status_code == 403
    assert response.json()["error"] == "invalid_access_token"


def test_token_for_deleted_account(setup_db, client):
    ## account 99 does not exist; the token is otherwise perfectly valid
    headers = {"Authorization": f"Bearer {_token(_claims(sub='99'))}"}
    response = client.get("/accounts/me", headers=headers)
    assert response.status_code == 403
    assert response.json()["error"] == "invalid_access_token"
