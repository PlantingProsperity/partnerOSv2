"""Timeline routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from partner_os_v2.api.deps import get_current_user
from partner_os_v2.api.errors import error_responses
from partner_os_v2.db import get_db
from partner_os_v2.models import AuditEvent, User
from partner_os_v2.schemas import TimelineEventOut

router = APIRouter(prefix="/api/v1", tags=["timeline"])


@router.get("/timeline", response_model=list[TimelineEventOut], responses=error_responses(401))
def list_timeline(
    entity_type: str | None = None,
    entity_id: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[TimelineEventOut]:
    query = select(AuditEvent)
    if entity_type:
        query = query.where(AuditEvent.entity_type == entity_type)
    if entity_id:
        query = query.where(AuditEvent.entity_id == entity_id)
    query = query.order_by(AuditEvent.created_at.desc()).limit(limit)

    rows = db.scalars(query).all()
    return [TimelineEventOut.model_validate(row, from_attributes=True) for row in rows]
