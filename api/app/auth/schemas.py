from pydantic import BaseModel, EmailStr


class AuthRegisterRequest(BaseModel):
    email: EmailStr
    password: str


class AuthLoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    plan: str
    analyses_used_this_month: int
    is_admin: bool
    is_active: bool
    created_at: str


class ErrorResponse(BaseModel):
    code: str
    message: str
