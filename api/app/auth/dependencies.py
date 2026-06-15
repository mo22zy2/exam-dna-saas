from fastapi import Cookie, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.utils import decode_access_token
from app.database import SessionLocal
from app.models.user import User


def get_current_user(
    access_token: str | None = Cookie(default=None),
) -> User:
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    user_id = decode_access_token(access_token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )
        return user
    finally:
        db.close()
