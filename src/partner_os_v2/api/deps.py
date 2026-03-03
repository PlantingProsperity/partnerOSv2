"""FastAPI dependencies for auth and authorization."""

from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from partner_os_v2.config import Settings, get_settings
from partner_os_v2.db import get_db
from partner_os_v2.models import User
from partner_os_v2.services.auth import AuthError, resolve_user_from_token

_bearer = HTTPBearer(auto_error=False)


def get_app_settings() -> Settings:
    return get_settings()


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_app_settings),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    try:
        return resolve_user_from_token(db, settings, credentials.credentials)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc


def require_roles(*roles: str):
    def checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user

    return checker
