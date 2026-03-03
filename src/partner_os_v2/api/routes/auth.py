"""Auth routes."""

from __future__ import annotations

from fastapi import APIRouter, Body, Depends, status
from sqlalchemy.orm import Session

from partner_os_v2.api.errors import api_error, error_responses
from partner_os_v2.api.deps import get_app_settings
from partner_os_v2.config import Settings
from partner_os_v2.db import get_db
from partner_os_v2.schemas import ErrorCode, LoginRequest, TokenResponse
from partner_os_v2.services.auth import AuthError, authenticate, create_access_token

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post(
    "/login",
    response_model=TokenResponse,
    responses=error_responses(401),
)
def login(
    payload: LoginRequest = Body(
        ...,
        openapi_examples={
            "default": {
                "summary": "Admin Login",
                "value": {"username": "admin", "password": "admin123"},
            }
        },
    ),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_app_settings),
) -> TokenResponse:
    try:
        user = authenticate(db, settings, payload.username, payload.password)
    except AuthError as exc:
        raise api_error(status.HTTP_401_UNAUTHORIZED, ErrorCode.UNAUTHORIZED, str(exc)) from exc

    token = create_access_token(settings, user)
    return TokenResponse(access_token=token, expires_in=settings.token_ttl_seconds)
