import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User, RefreshToken
from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.config import settings
from app.schemas.auth import UserRegisterRequest, UserLoginRequest, TokenResponse


def register_user(db: Session, data: UserRegisterRequest) -> User:
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email sudah terdaftar",
        )
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username sudah digunakan",
        )

    user = User(
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login_user(db: Session, data: UserLoginRequest) -> TokenResponse:
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email atau password salah",
        )

    access_token = create_access_token({"sub": str(user.id)})
    raw_refresh = create_refresh_token({"sub": str(user.id)})

    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    db_token = RefreshToken(
        user_id=user.id,
        token=raw_refresh,
        expires_at=expires_at,
    )
    db.add(db_token)
    db.commit()

    return TokenResponse(access_token=access_token, refresh_token=raw_refresh)


def refresh_access_token(db: Session, refresh_token: str) -> dict:
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token tidak valid",
        )

    db_token = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.token == refresh_token,
            RefreshToken.is_revoked == False,
        )
        .first()
    )
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token tidak ditemukan atau sudah direvoke",
        )

    if db_token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token sudah kadaluarsa",
        )

    user_id = payload.get("sub")
    new_access_token = create_access_token({"sub": user_id})
    return {"access_token": new_access_token, "token_type": "bearer"}


def logout_user(db: Session, refresh_token: str) -> None:
    db_token = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()
    if db_token:
        db_token.is_revoked = True
        db.commit()
