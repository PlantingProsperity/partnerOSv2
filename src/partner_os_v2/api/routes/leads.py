"""Lead routes."""

from __future__ import annotations

from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

from partner_os_v2.api.deps import get_app_settings, get_current_user
from partner_os_v2.api.errors import error_responses, workflow_http_error
from partner_os_v2.config import Settings
from partner_os_v2.db import get_db
from partner_os_v2.models import Lead, User
from partner_os_v2.schemas import LeadCreate, LeadOut, TransitionRequest
from partner_os_v2.services.audit import log_event
from partner_os_v2.services.workflow import WorkflowError, transition_entity

router = APIRouter(prefix="/api/v1/leads", tags=["leads"])


@router.post(
    "",
    response_model=LeadOut,
    responses=error_responses(401),
)
def create_lead(
    payload: LeadCreate = Body(
        ...,
        openapi_examples={
            "default": {
                "summary": "Create lead",
                "value": {
                    "source": "referral",
                    "name": "Alice Seller",
                    "phone": "+1-360-555-0000",
                    "email": "alice@example.com",
                    "address": "123 Main St, Vancouver, WA 98660",
                },
            }
        },
    ),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> LeadOut:
    lead = Lead(
        source=payload.source,
        name=payload.name,
        phone=payload.phone,
        email=payload.email,
        address=payload.address,
        parcel_id=payload.parcel_id,
        motivation_level=payload.motivation_level,
        pain_points=payload.pain_points,
        timeline=payload.timeline,
        assigned_to=payload.assigned_to,
        status="new",
    )
    db.add(lead)
    db.flush()
    log_event(
        db,
        event_type="lead_created",
        actor_type="user",
        actor_id=user.user_id,
        entity_type="lead",
        entity_id=lead.lead_id,
        payload={"source": lead.source},
    )
    db.commit()
    db.refresh(lead)
    return LeadOut.model_validate(lead, from_attributes=True)


@router.post(
    "/{lead_id}/transitions",
    response_model=LeadOut,
    responses=error_responses(401, 404, 409, 503),
)
def transition_lead(
    lead_id: str,
    payload: TransitionRequest = Body(
        ...,
        openapi_examples={
            "default": {
                "summary": "Lead state transition",
                "value": {
                    "to_state": "attempted_contact",
                    "recommendation_id": "b5a0c7b6-0896-4f20-8f16-e93a4f3a3476",
                    "reason": "AI recommended outreach",
                },
            }
        },
    ),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_app_settings),
    user: User = Depends(get_current_user),
) -> LeadOut:
    try:
        lead = transition_entity(
            db,
            settings=settings,
            entity_type="lead",
            entity_id=lead_id,
            to_state=payload.to_state,
            recommendation_id=payload.recommendation_id,
            reason=payload.reason,
            actor_id=user.user_id,
            actor_role=user.role,
        )
    except WorkflowError as exc:
        raise workflow_http_error(str(exc)) from exc

    db.commit()
    db.refresh(lead)
    return LeadOut.model_validate(lead, from_attributes=True)
