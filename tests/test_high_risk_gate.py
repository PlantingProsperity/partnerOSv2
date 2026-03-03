from __future__ import annotations

import pytest

from partner_os_v2.models import AIRecommendation, AISession, ApprovalGate, Deal
from partner_os_v2.services.workflow import WorkflowError, transition_entity


def test_high_risk_transition_requires_approval_gate(db_session):
    db, settings = db_session

    deal = Deal(property_address="123 Main St, Vancouver, WA", stage="drafting_structuring")
    db.add(deal)
    db.flush()

    ai_session = AISession(
        entity_type="deal",
        entity_id=deal.deal_id,
        context_hash="ctx",
        prompt_version="v1",
        created_by="user-1",
    )
    db.add(ai_session)
    db.flush()

    recommendation = AIRecommendation(
        session_id=ai_session.session_id,
        action="deal_mark_dead",
        rationale="Risk profile exceeds thresholds",
        confidence=0.90,
        risk_flags=["high_risk"],
        model_name="mock",
        model_version="v0",
        prompt_hash="hash",
        raw_output={"ok": True},
    )
    db.add(recommendation)
    db.flush()

    with pytest.raises(WorkflowError, match="Approval gate required"):
        transition_entity(
            db,
            settings=settings,
            entity_type="deal",
            entity_id=deal.deal_id,
            to_state="dead",
            recommendation_id=recommendation.recommendation_id,
            reason="Terminate deal",
            actor_id="user-1",
            actor_role="manager",
        )

    gate = ApprovalGate(
        recommendation_id=recommendation.recommendation_id,
        required_role="manager",
        decision="approved",
        decision_reason="Principal approved",
        decided_by="user-1",
    )
    db.add(gate)
    db.flush()

    transitioned = transition_entity(
        db,
        settings=settings,
        entity_type="deal",
        entity_id=deal.deal_id,
        to_state="dead",
        recommendation_id=recommendation.recommendation_id,
        reason="Terminate deal",
        actor_id="user-1",
        actor_role="manager",
    )
    db.commit()

    assert transitioned.stage == "dead"
