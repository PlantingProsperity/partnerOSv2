"""Audit event logging helpers."""

from __future__ import annotations

from sqlalchemy.orm import Session

from partner_os_v2.models import AuditEvent


def log_event(
    db: Session,
    *,
    event_type: str,
    actor_type: str,
    actor_id: str,
    entity_type: str,
    entity_id: str,
    payload: dict,
) -> AuditEvent:
    event = AuditEvent(
        event_type=event_type,
        actor_type=actor_type,
        actor_id=actor_id,
        entity_type=entity_type,
        entity_id=entity_id,
        payload_json=payload,
    )
    db.add(event)
    return event
