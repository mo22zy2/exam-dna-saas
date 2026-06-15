from fastapi import APIRouter, HTTPException, Response, status
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.schemas import (
    AuthRegisterRequest,
    UserResponse,
)
from app.auth.utils import create_access_token
from app.database import SessionLocal
from app.models.user import User

router = APIRouter(prefix="/auth")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _user_to_response(user: User) -> UserResponse:
    return UserResponse(
        id=str(user.id),
        email=user.email,
        plan=user.plan,
        analyses_used_this_month=user.analyses_used_this_month,
        is_admin=user.is_admin,
        is_active=user.is_active,
        created_at=user.created_at.isoformat(),
    )


def _set_token_cookie(response: Response, user_id: str) -> None:
    token = create_access_token(user_id)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=604800,
        samesite="lax",
        path="/",
    )


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(body: AuthRegisterRequest, response: Response):
    if len(body.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must be at least 8 characters",
        )

    db: Session = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == body.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

        is_first = db.query(User).count() == 0

        user = User(
            email=body.email,
            password_hash=pwd_context.hash(body.password),
            is_admin=is_first,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        _set_token_cookie(response, str(user.id))

        return {"success": True, "data": _user_to_response(user)}
    finally:
        db.close()
