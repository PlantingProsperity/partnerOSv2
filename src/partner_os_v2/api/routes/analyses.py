"""Analysis routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from partner_os_v2.api.deps import get_app_settings, get_current_user
from partner_os_v2.config import Settings
from partner_os_v2.db import get_db
from partner_os_v2.models import Analysis, User
from partner_os_v2.schemas import AnalysisCreate, AnalysisDecisionRequest, AnalysisOut
from partner_os_v2.services.audit import log_event
from partner_os_v2.services.workflow import WorkflowError, require_recommendation_exists, transition_entity

router = APIRouter(prefix="/api/v1/analyses", tags=["analyses"])


@router.post("", response_model=AnalysisOut)
def create_analysis(
    payload: AnalysisCreate,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_app_settings),
    user: User = Depends(get_current_user),
) -> AnalysisOut:
    if settings.require_ai_recommendation and not payload.recommendation_id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Recommendation required")
    if payload.recommendation_id:
        try:
            require_recommendation_exists(db, payload.recommendation_id)
        except WorkflowError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    analysis = Analysis(
        lead_id=payload.lead_id,
        arv=payload.arv,
        as_is_value=payload.as_is_value,
        rehab_budget=payload.rehab_budget,
        cap_rate=payload.cap_rate,
        cash_on_cash=payload.cash_on_cash,
        target_offer_price=payload.target_offer_price,
        max_offer_price=payload.max_offer_price,
        notes=payload.notes,
        status="draft",
    )
    db.add(analysis)
    db.flush()
    log_event(
        db,
        event_type="analysis_created",
        actor_type="user",
        actor_id=user.user_id,
        entity_type="analysis",
        entity_id=analysis.analysis_id,
        payload={"lead_id": analysis.lead_id, "recommendation_id": payload.recommendation_id},
    )
    db.commit()
    db.refresh(analysis)
    return AnalysisOut.model_validate(analysis, from_attributes=True)


@router.post("/{analysis_id}/decision", response_model=AnalysisOut)
def decide_analysis(
    analysis_id: str,
    payload: AnalysisDecisionRequest,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_app_settings),
    user: User = Depends(get_current_user),
) -> AnalysisOut:
    try:
        analysis = transition_entity(
            db,
            settings=settings,
            entity_type="analysis",
            entity_id=analysis_id,
            to_state=payload.status,
            recommendation_id=payload.recommendation_id,
            reason=payload.reason,
            actor_id=user.user_id,
            actor_role=user.role,
        )
    except WorkflowError as exc:
        msg = str(exc)
        if msg.startswith("DEGRADED:"):
            blocked_id = msg.split(":", maxsplit=1)[1]
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={"code": "degraded_mode", "blocked_action_id": blocked_id},
            ) from exc
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg) from exc

    db.commit()
    db.refresh(analysis)
    return AnalysisOut.model_validate(analysis, from_attributes=True)
