"""Auth routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from partner_os_v2.api.deps import get_app_settings
from partner_os_v2.config import Settings
from partner_os_v2.db import get_db
from partner_os_v2.schemas import LoginRequest, TokenResponse
from partner_os_v2.services.auth import AuthError, authenticate, create_access_token

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db), settings: Settings = Depends(get_app_settings)) -> TokenResponse:
    try:
        user = authenticate(db, settings, payload.username, payload.password)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    token = create_access_token(settings, user)
    return TokenResponse(access_token=token, expires_in=settings.token_ttl_seconds)
