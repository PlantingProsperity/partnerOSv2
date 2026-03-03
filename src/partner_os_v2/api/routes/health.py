"""Health route."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from partner_os_v2.db import get_db
from partner_os_v2.schemas import HealthOut
from partner_os_v2.services.ai_gateway import blocked_count, get_ai_state

router = APIRouter(prefix="/api/v1", tags=["health"])


@router.get("/health", response_model=HealthOut)
def health(db: Session = Depends(get_db)) -> HealthOut:
    return HealthOut(
        status="ok",
        ai_state=get_ai_state(db),
        blocked_actions_queued=blocked_count(db),
    )
