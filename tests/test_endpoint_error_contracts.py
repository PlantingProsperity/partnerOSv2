from __future__ import annotations

import pytest
from fastapi import HTTPException

from partner_os_v2.api.deps import get_current_user, require_roles
from partner_os_v2.api.routes.ai import create_recommendation
from partner_os_v2.api.routes.leads import transition_lead
from partner_os_v2.models import AISession, Lead, User
from partner_os_v2.schemas import AIRecommendationCreate, TransitionRequest
from partner_os_v2.services.ai_gateway import blocked_count, get_ai_state


def _admin_user(db) -> User:
    admin = db.query(User).filter(User.username == "admin").one_or_none()
    assert admin is not None
    return admin


def test_401_missing_token_returns_standard_error(db_session):
    db, settings = db_session

    with pytest.raises(HTTPException) as exc:
        get_current_user(credentials=None, db=db, settings=settings)

    assert exc.value.status_code == 401
    assert exc.value.detail["error"]["code"] == "unauthorized"


def test_403_non_manager_cannot_approve_contract(db_session):
    db, _settings = db_session

    user = User(username="operator", password_hash="x", role="acquisition", is_active=True)
    db.add(user)
    db.flush()

    checker = require_roles("admin", "manager")
    with pytest.raises(HTTPException) as exc:
        checker(user=user)

    assert exc.value.status_code == 403
    assert exc.value.detail["error"]["code"] == "forbidden"


def test_409_recommendation_required_contract(db_session):
    db, settings = db_session
    admin = _admin_user(db)

    lead = Lead(source="referral", name="Alice Seller", status="new")
    db.add(lead)
    db.flush()

    payload = TransitionRequest(to_state="attempted_contact", recommendation_id=None, reason="No AI")
    with pytest.raises(HTTPException) as exc:
        transition_lead(lead_id=lead.lead_id, payload=payload, db=db, settings=settings, user=admin)

    assert exc.value.status_code == 409
    assert exc.value.detail["error"]["code"] == "recommendation_required"


def test_503_ai_runtime_unavailable_contract(db_session):
    db, settings = db_session
    admin = _admin_user(db)

    lead = Lead(source="call", name="Carol Seller", status="new")
    db.add(lead)
    db.flush()

    ai_session = AISession(
        entity_type="lead",
        entity_id=lead.lead_id,
        context_hash="ctx",
        prompt_version="v1",
        created_by=admin.user_id,
    )
    db.add(ai_session)
    db.flush()

    down_settings = settings.model_copy(update={"ai_mode": "gemini", "gemini_api_key": ""})
    payload = AIRecommendationCreate(
        session_id=ai_session.session_id,
        action="lead_transition_attempted_contact",
        context_override={"note": "contact now"},
    )

    with pytest.raises(HTTPException) as exc:
        create_recommendation(payload=payload, db=db, settings=down_settings, user=admin)

    assert exc.value.status_code == 503
    assert exc.value.detail["error"]["code"] == "ai_runtime_unavailable"
    assert exc.value.detail["error"]["meta"]["blocked_action_id"]
    assert get_ai_state(db) == "degraded"
    assert blocked_count(db) >= 1
