from typing import cast
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.config import settings


def create_access_token(user_id: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "iat": now,
        "exp": now + timedelta(seconds=settings.jwt_expiry),
    }
    return cast(str, jwt.encode(payload, settings.jwt_secret, algorithm="HS256"))


def decode_access_token(token: str) -> str | None:
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=["HS256"]
        )
        return cast(str | None, payload.get("sub"))
    except JWTError:
        return None
