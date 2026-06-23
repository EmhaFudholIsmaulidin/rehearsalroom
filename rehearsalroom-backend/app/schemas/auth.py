from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator


class UserRegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Username minimal 3 karakter")
        if len(v) > 50:
            raise ValueError("Username maksimal 50 karakter")
        return v

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password minimal 8 karakter")
        return v


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}
