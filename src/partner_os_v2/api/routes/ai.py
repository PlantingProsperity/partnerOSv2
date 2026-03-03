"""AI session and recommendation routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from partner_os_v2.api.deps import get_app_settings, get_current_user, require_roles
from partner_os_v2.config import Settings
from partner_os_v2.domain import is_high_risk
from partner_os_v2.db import get_db
from partner_os_v2.models import AIRecommendation, AISession, ApprovalGate, User
from partner_os_v2.schemas import (
    AIRecommendationCreate,
    AIRecommendationOut,
    AISessionCreate,
    AISessionOut,
    ApprovalDecisionRequest,
    ApprovalGateOut,
)
from partner_os_v2.services.ai_gateway import (
    AIResponseError,
    AIRuntimeUnavailable,
    GeminiGateway,
    get_ai_state,
    hash_context,
    queue_blocked_action,
    set_ai_state,
)
from partner_os_v2.services.audit import log_event

router = APIRouter(prefix="/api/v1/ai", tags=["ai"])


@router.post("/sessions", response_model=AISessionOut)
def create_session(
    payload: AISessionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> AISessionOut:
    session = AISession(
        entity_type=payload.entity_type,
        entity_id=payload.entity_id,
        context_hash=hash_context(payload.context_payload),
        prompt_version=payload.prompt_version,
        created_by=user.user_id,
    )
    db.add(session)
    db.flush()
    log_event(
        db,
        event_type="ai_session_created",
        actor_type="user",
        actor_id=user.user_id,
        entity_type=payload.entity_type,
        entity_id=payload.entity_id,
        payload={"session_id": session.session_id, "prompt_version": payload.prompt_version},
    )
    db.commit()
    db.refresh(session)
    return AISessionOut.model_validate(session, from_attributes=True)


@router.post("/recommendations", response_model=AIRecommendationOut)
def create_recommendation(
    payload: AIRecommendationCreate,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_app_settings),
    user: User = Depends(get_current_user),
) -> AIRecommendationOut:
    ai_session = db.get(AISession, payload.session_id)
    if ai_session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AI session not found")

    gateway = GeminiGateway(settings)
    try:
        generated = gateway.generate(
            ai_session=ai_session,
            action=payload.action,
            context_payload=payload.context_override,
        )
    except AIRuntimeUnavailable as exc:
        set_ai_state(db, "degraded")
        blocked = queue_blocked_action(
            db,
            action_type="generate_recommendation",
            entity_type=ai_session.entity_type,
            entity_id=ai_session.entity_id,
            payload_json={"session_id": ai_session.session_id, "action": payload.action},
            reason=str(exc),
            created_by=user.user_id,
        )
        log_event(
            db,
            event_type="ai_recommendation_blocked",
            actor_type="system",
            actor_id=user.user_id,
            entity_type=ai_session.entity_type,
            entity_id=ai_session.entity_id,
            payload={"blocked_action_id": blocked.blocked_action_id, "reason": str(exc)},
        )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "ai_runtime_unavailable",
                "message": str(exc),
                "blocked_action_id": blocked.blocked_action_id,
            },
        ) from exc
    except AIResponseError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    set_ai_state(db, "normal")
    recommendation = AIRecommendation(
        session_id=ai_session.session_id,
        action=generated["action"],
        rationale=generated["rationale"],
        confidence=generated["confidence"],
        risk_flags=generated["risk_flags"],
        model_name=generated["model_name"],
        model_version=generated["model_version"],
        prompt_hash=generated["prompt_hash"],
        raw_output=generated["raw_output"],
    )
    db.add(recommendation)
    db.flush()

    approval_required = is_high_risk(ai_session.entity_type, recommendation.action, to_state="")
    if approval_required:
        gate = ApprovalGate(
            recommendation_id=recommendation.recommendation_id,
            required_role="manager",
            decision="pending",
        )
        db.add(gate)

    log_event(
        db,
        event_type="ai_recommendation_created",
        actor_type="ai",
        actor_id=user.user_id,
        entity_type=ai_session.entity_type,
        entity_id=ai_session.entity_id,
        payload={"recommendation_id": recommendation.recommendation_id, "action": recommendation.action},
    )
    db.commit()
    db.refresh(recommendation)

    return AIRecommendationOut(
        recommendation_id=recommendation.recommendation_id,
        session_id=recommendation.session_id,
        action=recommendation.action,
        rationale=recommendation.rationale,
        confidence=recommendation.confidence,
        risk_flags=[str(x) for x in recommendation.risk_flags],
        status=recommendation.status,
        model_name=recommendation.model_name,
        model_version=recommendation.model_version,
        prompt_hash=recommendation.prompt_hash,
        approval_required=approval_required,
        created_at=recommendation.created_at,
    )


@router.post("/recommendations/{recommendation_id}/approve", response_model=ApprovalGateOut)
def approve_recommendation(
    recommendation_id: str,
    payload: ApprovalDecisionRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin", "manager")),
) -> ApprovalGateOut:
    gate = db.scalar(select(ApprovalGate).where(ApprovalGate.recommendation_id == recommendation_id))
    if gate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval gate not found")

    if payload.decision not in {"approved", "rejected"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Decision must be approved or rejected")

    gate.decision = payload.decision
    gate.decision_reason = payload.reason
    gate.decided_by = user.user_id
    from datetime import datetime, timezone

    gate.decided_at = datetime.now(timezone.utc)

    recommendation = db.get(AIRecommendation, recommendation_id)
    if recommendation is not None:
        recommendation.status = "approved" if payload.decision == "approved" else "rejected"

    session = db.get(AISession, recommendation.session_id) if recommendation else None
    log_event(
        db,
        event_type="approval_gate_decided",
        actor_type="user",
        actor_id=user.user_id,
        entity_type=session.entity_type if session else "ai_recommendation",
        entity_id=session.entity_id if session else recommendation_id,
        payload={
            "recommendation_id": recommendation_id,
            "decision": payload.decision,
            "reason": payload.reason,
        },
    )
    db.commit()
    db.refresh(gate)
    return ApprovalGateOut.model_validate(gate, from_attributes=True)


@router.get("/sessions/{session_id}")
def get_session(
    session_id: str,
    include_recommendations: bool = Query(default=True),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    ai_session = db.get(AISession, session_id)
    if ai_session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AI session not found")

    body = {
        "session": AISessionOut.model_validate(ai_session, from_attributes=True).model_dump(),
        "ai_state": get_ai_state(db),
    }
    if include_recommendations:
        recs = db.scalars(
            select(AIRecommendation).where(AIRecommendation.session_id == session_id).order_by(AIRecommendation.created_at.desc())
        ).all()
        body["recommendations"] = [
            AIRecommendationOut(
                recommendation_id=r.recommendation_id,
                session_id=r.session_id,
                action=r.action,
                rationale=r.rationale,
                confidence=r.confidence,
                risk_flags=[str(x) for x in r.risk_flags],
                status=r.status,
                model_name=r.model_name,
                model_version=r.model_version,
                prompt_hash=r.prompt_hash,
                approval_required=db.scalar(select(ApprovalGate).where(ApprovalGate.recommendation_id == r.recommendation_id))
                is not None,
                created_at=r.created_at,
            ).model_dump()
            for r in recs
        ]
    return body
