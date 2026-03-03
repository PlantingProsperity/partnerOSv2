"""Analysis routes."""

from __future__ import annotations

from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

from partner_os_v2.api.deps import get_app_settings, get_current_user
from partner_os_v2.api.errors import error_responses, workflow_http_error
from partner_os_v2.config import Settings
from partner_os_v2.db import get_db
from partner_os_v2.models import Analysis, User
from partner_os_v2.schemas import AnalysisCreate, AnalysisDecisionRequest, AnalysisOut
from partner_os_v2.services.audit import log_event
from partner_os_v2.services.workflow import WorkflowError, require_recommendation_exists, transition_entity

router = APIRouter(prefix="/api/v1/analyses", tags=["analyses"])


@router.post(
    "",
    response_model=AnalysisOut,
    responses=error_responses(401, 409),
)
def create_analysis(
    payload: AnalysisCreate = Body(
        ...,
        openapi_examples={
            "default": {
                "summary": "Create analysis",
                "value": {
                    "lead_id": "4a21b4ec-e8c0-4df2-bf6b-aaf5de3d01f0",
                    "arv": 420000,
                    "rehab_budget": 60000,
                    "recommendation_id": "b6bb98fe-dd03-40f0-9010-3f46e46d8bcf",
                },
            }
        },
    ),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_app_settings),
    user: User = Depends(get_current_user),
) -> AnalysisOut:
    if settings.require_ai_recommendation and not payload.recommendation_id:
        raise workflow_http_error("Recommendation required")
    if payload.recommendation_id:
        try:
            require_recommendation_exists(db, payload.recommendation_id)
        except WorkflowError as exc:
            raise workflow_http_error(str(exc)) from exc

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


@router.post(
    "/{analysis_id}/decision",
    response_model=AnalysisOut,
    responses=error_responses(401, 404, 409, 503),
)
def decide_analysis(
    analysis_id: str,
    payload: AnalysisDecisionRequest = Body(
        ...,
        openapi_examples={
            "default": {
                "summary": "Analysis decision transition",
                "value": {
                    "status": "under_review",
                    "recommendation_id": "12d30ab8-cfe8-46d5-b855-449677815c95",
                    "reason": "Ready for principal review",
                },
            }
        },
    ),
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
        raise workflow_http_error(str(exc)) from exc

    db.commit()
    db.refresh(analysis)
    return AnalysisOut.model_validate(analysis, from_attributes=True)
