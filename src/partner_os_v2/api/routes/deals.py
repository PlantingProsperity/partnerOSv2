"""Deal routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from partner_os_v2.api.deps import get_app_settings, get_current_user
from partner_os_v2.config import Settings
from partner_os_v2.db import get_db
from partner_os_v2.models import Deal, User
from partner_os_v2.schemas import DealCreate, DealOut, TransitionRequest
from partner_os_v2.services.audit import log_event
from partner_os_v2.services.workflow import WorkflowError, require_recommendation_exists, transition_entity

router = APIRouter(prefix="/api/v1/deals", tags=["deals"])


@router.post("", response_model=DealOut)
def create_deal(
    payload: DealCreate,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_app_settings),
    user: User = Depends(get_current_user),
) -> DealOut:
    if settings.require_ai_recommendation and not payload.recommendation_id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Recommendation required")
    if payload.recommendation_id:
        try:
            require_recommendation_exists(db, payload.recommendation_id)
        except WorkflowError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    deal = Deal(
        analysis_id=payload.analysis_id,
        property_address=payload.property_address,
        purchase_price=payload.purchase_price,
        earnest_money=payload.earnest_money,
        financing_type=payload.financing_type,
        stage="drafting_structuring",
    )
    db.add(deal)
    db.flush()
    log_event(
        db,
        event_type="deal_created",
        actor_type="user",
        actor_id=user.user_id,
        entity_type="deal",
        entity_id=deal.deal_id,
        payload={"analysis_id": deal.analysis_id, "recommendation_id": payload.recommendation_id},
    )
    db.commit()
    db.refresh(deal)
    return DealOut.model_validate(deal, from_attributes=True)


@router.post("/{deal_id}/stages", response_model=DealOut)
def transition_deal(
    deal_id: str,
    payload: TransitionRequest,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_app_settings),
    user: User = Depends(get_current_user),
) -> DealOut:
    try:
        deal = transition_entity(
            db,
            settings=settings,
            entity_type="deal",
            entity_id=deal_id,
            to_state=payload.to_state,
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
    db.refresh(deal)
    return DealOut.model_validate(deal, from_attributes=True)
