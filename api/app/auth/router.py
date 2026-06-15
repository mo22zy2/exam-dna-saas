from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import RedirectResponse
from httpx_oauth.clients.google import GoogleOAuth2
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.schemas import (
    AuthLoginRequest,
    AuthRegisterRequest,
    UserResponse,
)
from app.auth.utils import create_access_token
from app.config import settings
from app.database import SessionLocal
from app.models.oauth_identity import OAuthIdentity
from app.models.user import User

router = APIRouter(prefix="/auth")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

google_client = GoogleOAuth2(
    settings.google_client_id, settings.google_client_secret
)


GOOGLE_REDIRECT_URI = "http://localhost:8000/auth/google/callback"
FRONTEND_URL = "http://localhost:3000"


@router.get("/google")
async def google_login():
    authorization_url = await google_client.get_authorization_url(
        GOOGLE_REDIRECT_URI,
        scope=["openid", "email", "profile"],
    )
    return RedirectResponse(authorization_url, status_code=302)


@router.get("/google/callback")
async def google_callback(
    code: str | None = Query(default=None),
    error: str | None = Query(default=None),
):
    if error:
        return RedirectResponse(
            f"{FRONTEND_URL}/login?error=access_denied", status_code=302
        )

    if not code:
        return RedirectResponse(
            f"{FRONTEND_URL}/login?error=missing_code", status_code=302
        )

    token = await google_client.get_access_token(code, GOOGLE_REDIRECT_URI)
    id_token = token.get("id_token")
    if not id_token:
        return RedirectResponse(
            f"{FRONTEND_URL}/login?error=no_id_token", status_code=302
        )

    payload = jwt.get_unverified_claims(id_token)
    email = payload.get("email")
    google_sub = payload.get("sub")
    if not email or not google_sub:
        return RedirectResponse(
            f"{FRONTEND_URL}/login?error=invalid_token", status_code=302
        )

    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            is_first = db.query(User).count() == 0
            user = User(email=email, is_admin=is_first)
            db.add(user)
            db.flush()

        identity = db.query(OAuthIdentity).filter(
            OAuthIdentity.provider == "google",
            OAuthIdentity.provider_user_id == google_sub,
        ).first()
        if not identity:
            identity = OAuthIdentity(
                user_id=user.id,
                provider="google",
                provider_user_id=google_sub,
            )
            db.add(identity)

        db.commit()
        db.refresh(user)

        response = RedirectResponse(FRONTEND_URL, status_code=302)
        _set_token_cookie(response, str(user.id))
        return response
    except Exception:
        db.rollback()
        return RedirectResponse(
            f"{FRONTEND_URL}/login?error=server_error", status_code=302
        )
    finally:
        db.close()


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {"success": True, "data": _user_to_response(current_user)}


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


@router.post("/jwt/login")
async def login(body: AuthLoginRequest, response: Response):
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.email == body.email).first()
        if not user or not user.password_hash:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not pwd_context.verify(body.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is inactive",
            )

        _set_token_cookie(response, str(user.id))

        return {"success": True, "data": _user_to_response(user)}
    finally:
        db.close()


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


@router.post("/logout")
async def logout(response: Response):
    response.set_cookie(
        key="access_token",
        value="",
        httponly=True,
        max_age=0,
        samesite="lax",
        path="/",
    )
    return {
        "success": True,
        "data": {"message": "Logged out successfully"},
    }
