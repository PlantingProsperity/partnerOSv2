"""Authentication and user helpers."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from partner_os_v2.config import Settings
from partner_os_v2.models import User
from partner_os_v2.security import hash_password, issue_token, verify_password, verify_token


class AuthError(RuntimeError):
    """Raised on authentication failures."""


def ensure_admin_user(db: Session, settings: Settings) -> None:
    existing = db.scalar(select(User).where(User.username == settings.admin_username))
    if existing:
        return

    admin = User(
        username=settings.admin_username,
        password_hash=hash_password(settings.admin_password),
        role="admin",
        is_active=True,
    )
    db.add(admin)
    db.commit()


def authenticate(db: Session, settings: Settings, username: str, password: str) -> User:
    user = db.scalar(select(User).where(User.username == username))
    if not user or not user.is_active:
        raise AuthError("Invalid credentials")
    if not verify_password(password, user.password_hash):
        raise AuthError("Invalid credentials")
    return user


def create_access_token(settings: Settings, user: User) -> str:
    payload = {
        "sub": user.user_id,
        "username": user.username,
        "role": user.role,
    }
    return issue_token(settings.token_secret, payload)


def resolve_user_from_token(db: Session, settings: Settings, token: str) -> User:
    try:
        payload = verify_token(settings.token_secret, token, settings.token_ttl_seconds)
    except ValueError as exc:
        raise AuthError(str(exc)) from exc

    user_id = str(payload.get("sub", ""))
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise AuthError("Invalid credentials")
    return user
