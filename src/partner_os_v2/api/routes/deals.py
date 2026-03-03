"""Deal routes."""

from __future__ import annotations

from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

from partner_os_v2.api.deps import get_app_settings, get_current_user
from partner_os_v2.api.errors import error_responses, workflow_http_error
from partner_os_v2.config import Settings
from partner_os_v2.db import get_db
from partner_os_v2.models import Deal, User
from partner_os_v2.schemas import DealCreate, DealOut, TransitionRequest
from partner_os_v2.services.audit import log_event
from partner_os_v2.services.workflow import WorkflowError, require_recommendation_exists, transition_entity

router = APIRouter(prefix="/api/v1/deals", tags=["deals"])


@router.post(
    "",
    response_model=DealOut,
    responses=error_responses(401, 409),
)
def create_deal(
    payload: DealCreate = Body(
        ...,
        openapi_examples={
            "default": {
                "summary": "Create deal",
                "value": {
                    "analysis_id": "0a2f7106-e028-42a0-883b-3354c2a5eec6",
                    "property_address": "123 Main St, Vancouver, WA 98660",
                    "purchase_price": 325000,
                    "recommendation_id": "56ce4846-8fac-419f-9cbc-32f5f9f709af",
                },
            }
        },
    ),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_app_settings),
    user: User = Depends(get_current_user),
) -> DealOut:
    if settings.require_ai_recommendation and not payload.recommendation_id:
        raise workflow_http_error("Recommendation required")
    if payload.recommendation_id:
        try:
            require_recommendation_exists(db, payload.recommendation_id)
        except WorkflowError as exc:
            raise workflow_http_error(str(exc)) from exc

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


@router.post(
    "/{deal_id}/stages",
    response_model=DealOut,
    responses=error_responses(401, 404, 409, 503),
)
def transition_deal(
    deal_id: str,
    payload: TransitionRequest = Body(
        ...,
        openapi_examples={
            "default": {
                "summary": "Deal stage transition",
                "value": {
                    "to_state": "negotiation",
                    "recommendation_id": "f2ca61c2-0ec6-4ea2-8047-5412b11ce52c",
                    "reason": "Offer package ready",
                },
            }
        },
    ),
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
        raise workflow_http_error(str(exc)) from exc

    db.commit()
    db.refresh(deal)
    return DealOut.model_validate(deal, from_attributes=True)
