"""Case routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from partner_os_v2.api.deps import get_app_settings, get_current_user
from partner_os_v2.config import Settings
from partner_os_v2.db import get_db
from partner_os_v2.models import Case, User
from partner_os_v2.schemas import CaseCreate, CaseOut, TransitionRequest
from partner_os_v2.services.audit import log_event
from partner_os_v2.services.workflow import WorkflowError, require_recommendation_exists, transition_entity

router = APIRouter(prefix="/api/v1/cases", tags=["cases"])


@router.post("", response_model=CaseOut)
def create_case(
    payload: CaseCreate,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_app_settings),
    user: User = Depends(get_current_user),
) -> CaseOut:
    if settings.require_ai_recommendation and not payload.recommendation_id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Recommendation required")
    if payload.recommendation_id:
        try:
            require_recommendation_exists(db, payload.recommendation_id)
        except WorkflowError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    case_obj = Case(
        linked_deal_id=payload.linked_deal_id,
        title=payload.title,
        case_type=payload.case_type,
        priority=payload.priority,
        severity=payload.severity,
        assigned_to=payload.assigned_to,
        status="new",
    )
    db.add(case_obj)
    db.flush()
    log_event(
        db,
        event_type="case_created",
        actor_type="user",
        actor_id=user.user_id,
        entity_type="case",
        entity_id=case_obj.case_id,
        payload={"linked_deal_id": case_obj.linked_deal_id, "recommendation_id": payload.recommendation_id},
    )
    db.commit()
    db.refresh(case_obj)
    return CaseOut.model_validate(case_obj, from_attributes=True)


@router.post("/{case_id}/transitions", response_model=CaseOut)
def transition_case(
    case_id: str,
    payload: TransitionRequest,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_app_settings),
    user: User = Depends(get_current_user),
) -> CaseOut:
    try:
        case_obj = transition_entity(
            db,
            settings=settings,
            entity_type="case",
            entity_id=case_id,
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
    db.refresh(case_obj)
    return CaseOut.model_validate(case_obj, from_attributes=True)
