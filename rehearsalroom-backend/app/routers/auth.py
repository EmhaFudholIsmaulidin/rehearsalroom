from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    AccessTokenResponse,
    RefreshTokenRequest,
    LogoutRequest,
    UserResponse,
)
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Daftarkan user baru",
)
def register(data: UserRegisterRequest, db: Session = Depends(get_db)):
    user = auth_service.register_user(db, data)
    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login dan dapatkan access + refresh token",
)
def login(data: UserLoginRequest, db: Session = Depends(get_db)):
    return auth_service.login_user(db, data)


@router.post(
    "/refresh",
    response_model=AccessTokenResponse,
    summary="Refresh access token menggunakan refresh token",
)
def refresh_token(data: RefreshTokenRequest, db: Session = Depends(get_db)):
    return auth_service.refresh_access_token(db, data.refresh_token)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout dan invalidate refresh token",
)
def logout(data: LogoutRequest, db: Session = Depends(get_db)):
    auth_service.logout_user(db, data.refresh_token)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Dapatkan profil user yang sedang login",
)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
