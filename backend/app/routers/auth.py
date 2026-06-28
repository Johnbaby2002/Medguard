from datetime import timedelta, timezone
import hashlib
import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.security import create_access_token, hash_password, verify_password
from app.database import get_db
from app.models import HealthProfile, PasswordResetToken, User, utc_now
from app.schemas import ForgotPasswordRequest, ForgotPasswordResponse, ResetPasswordRequest, TokenResponse, UserCreate, UserLogin, UserOut
from app.services.audit import log_audit

router = APIRouter(prefix="/auth", tags=["auth"])


def token_response(user: User) -> TokenResponse:
    token = create_access_token(subject=user.id, extra_claims={"email": user.email, "role": user.role.value})
    return TokenResponse(access_token=token, user=user)


def hash_reset_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Annotated[Session, Depends(get_db)]) -> TokenResponse:
    existing = db.scalar(select(User).where(User.email == payload.email.lower()))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
        phone_number=payload.phone_number,
        role=payload.role,
        terms_accepted_at=utc_now(),
        medical_disclaimer_accepted_at=utc_now(),
    )
    db.add(user)
    db.flush()
    db.add(HealthProfile(user_id=user.id, age=payload.age))
    log_audit(db, user, "register", "user", user.id)
    db.commit()
    db.refresh(user)
    return token_response(user)


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
def forgot_password(payload: ForgotPasswordRequest, db: Annotated[Session, Depends(get_db)]) -> ForgotPasswordResponse:
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    message = "If an account exists for this email, a password reset link has been created."
    if not user:
        return ForgotPasswordResponse(message=message, reset_token=None)

    raw_token = secrets.token_urlsafe(32)
    reset = PasswordResetToken(
        user_id=user.id,
        token_hash=hash_reset_token(raw_token),
        expires_at=utc_now() + timedelta(minutes=30),
    )
    db.add(reset)
    db.flush()
    log_audit(db, user, "forgot_password_requested", "password_reset_token", reset.id)
    db.commit()
    return ForgotPasswordResponse(message=message, reset_token=raw_token)


@router.post("/reset-password", response_model=TokenResponse)
def reset_password(payload: ResetPasswordRequest, db: Annotated[Session, Depends(get_db)]) -> TokenResponse:
    token_hash = hash_reset_token(payload.token)
    reset = db.scalar(select(PasswordResetToken).where(PasswordResetToken.token_hash == token_hash))
    if not reset or reset.used_at:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or used reset token")

    expires_at = reset.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < utc_now():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reset token has expired")

    user = db.get(User, reset.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid reset token")

    user.password_hash = hash_password(payload.password)
    reset.used_at = utc_now()
    db.flush()
    log_audit(db, user, "password_reset_completed", "user", user.id)
    db.commit()
    db.refresh(user)
    return token_response(user)


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Annotated[Session, Depends(get_db)]) -> TokenResponse:
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    log_audit(db, user, "login", "user", user.id)
    db.commit()
    return token_response(user)


@router.get("/me", response_model=UserOut)
def me(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    return current_user
