"""Workflow transition orchestration and gate enforcement."""

from __future__ import annotations

from sqlalchemy.orm import Session

from partner_os_v2.config import Settings
from partner_os_v2.domain import can_transition, is_high_risk
from partner_os_v2.models import AIRecommendation, AISession, Analysis, ApprovalGate, Case, Deal, Lead
from partner_os_v2.services.ai_gateway import get_ai_state, queue_blocked_action
from partner_os_v2.services.audit import log_event


class WorkflowError(RuntimeError):
    """Raised when workflow operation fails validation."""


def _get_entity(db: Session, entity_type: str, entity_id: str):
    model_map = {
        "lead": Lead,
        "analysis": Analysis,
        "deal": Deal,
        "case": Case,
    }
    model = model_map.get(entity_type)
    if model is None:
        raise WorkflowError(f"Unsupported entity_type: {entity_type}")

    entity = db.get(model, entity_id)
    if entity is None:
        raise WorkflowError(f"{entity_type} not found")
    return entity


def _state_field(entity_type: str) -> str:
    if entity_type == "deal":
        return "stage"
    return "status"


def _validate_recommendation(
    db: Session,
    *,
    recommendation_id: str,
    entity_type: str,
    entity_id: str,
    to_state: str,
) -> AIRecommendation:
    recommendation = db.get(AIRecommendation, recommendation_id)
    if recommendation is None:
        raise WorkflowError("Recommendation not found")

    if recommendation.status == "rejected":
        raise WorkflowError("Recommendation rejected")

    session = db.get(AISession, recommendation.session_id)
    if session and (session.entity_type != entity_type or session.entity_id != entity_id):
        raise WorkflowError("Recommendation does not match target entity")

    if is_high_risk(entity_type, recommendation.action, to_state):
        gate = db.query(ApprovalGate).filter(ApprovalGate.recommendation_id == recommendation.recommendation_id).one_or_none()
        if gate is None or gate.decision != "approved":
            raise WorkflowError("Approval gate required for high-risk transition")

    return recommendation


def require_recommendation_exists(db: Session, recommendation_id: str) -> AIRecommendation:
    recommendation = db.get(AIRecommendation, recommendation_id)
    if recommendation is None:
        raise WorkflowError("Recommendation not found")
    if recommendation.status == "rejected":
        raise WorkflowError("Recommendation rejected")
    return recommendation


def transition_entity(
    db: Session,
    *,
    settings: Settings,
    entity_type: str,
    entity_id: str,
    to_state: str,
    recommendation_id: str | None,
    reason: str,
    actor_id: str,
    actor_role: str,
):
    entity = _get_entity(db, entity_type, entity_id)
    state_field = _state_field(entity_type)
    from_state = getattr(entity, state_field)

    if not can_transition(entity_type, from_state, to_state):
        raise WorkflowError(f"Invalid transition {from_state} -> {to_state} for {entity_type}")

    if settings.require_ai_recommendation and not recommendation_id:
        if get_ai_state(db) == "degraded":
            blocked = queue_blocked_action(
                db,
                action_type=f"{entity_type}_transition",
                entity_type=entity_type,
                entity_id=entity_id,
                payload_json={"from_state": from_state, "to_state": to_state, "reason": reason},
                reason="AI runtime degraded; missing recommendation",
                created_by=actor_id,
            )
            db.flush()
            raise WorkflowError(f"DEGRADED:{blocked.blocked_action_id}")
        raise WorkflowError("Recommendation required")

    recommendation = None
    if recommendation_id:
        recommendation = _validate_recommendation(
            db,
            recommendation_id=recommendation_id,
            entity_type=entity_type,
            entity_id=entity_id,
            to_state=to_state,
        )

    setattr(entity, state_field, to_state)
    log_event(
        db,
        event_type=f"{entity_type}_transitioned",
        actor_type="user",
        actor_id=actor_id,
        entity_type=entity_type,
        entity_id=entity_id,
        payload={
            "from_state": from_state,
            "to_state": to_state,
            "reason": reason,
            "recommendation_id": recommendation.recommendation_id if recommendation else None,
            "actor_role": actor_role,
        },
    )
    db.flush()
    return entity
