from __future__ import annotations

import pytest

from partner_os_v2.models import AIRecommendation, AISession, Lead
from partner_os_v2.services.workflow import WorkflowError, transition_entity


def test_lead_transition_requires_recommendation(db_session):
    db, settings = db_session

    lead = Lead(source="referral", name="Alice Seller", status="new")
    db.add(lead)
    db.flush()

    with pytest.raises(WorkflowError, match="Recommendation required"):
        transition_entity(
            db,
            settings=settings,
            entity_type="lead",
            entity_id=lead.lead_id,
            to_state="attempted_contact",
            recommendation_id=None,
            reason="Initial outreach",
            actor_id="user-1",
            actor_role="manager",
        )

    ai_session = AISession(
        entity_type="lead",
        entity_id=lead.lead_id,
        context_hash="ctx",
        prompt_version="v1",
        created_by="user-1",
    )
    db.add(ai_session)
    db.flush()

    recommendation = AIRecommendation(
        session_id=ai_session.session_id,
        action="lead_transition_attempted_contact",
        rationale="Contact now",
        confidence=0.84,
        risk_flags=[],
        model_name="mock",
        model_version="v0",
        prompt_hash="hash",
        raw_output={"ok": True},
    )
    db.add(recommendation)
    db.flush()

    transitioned = transition_entity(
        db,
        settings=settings,
        entity_type="lead",
        entity_id=lead.lead_id,
        to_state="attempted_contact",
        recommendation_id=recommendation.recommendation_id,
        reason="AI recommendation accepted",
        actor_id="user-1",
        actor_role="manager",
    )
    db.commit()

    assert transitioned.status == "attempted_contact"
