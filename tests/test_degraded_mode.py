from __future__ import annotations

import pytest

from partner_os_v2.models import BlockedAction, Lead
from partner_os_v2.services.ai_gateway import set_ai_state
from partner_os_v2.services.workflow import WorkflowError, transition_entity


def test_degraded_mode_queues_blocked_transition(db_session):
    db, settings = db_session

    lead = Lead(source="call", name="Carol Seller", status="new")
    db.add(lead)
    db.flush()

    set_ai_state(db, "degraded")
    db.flush()

    with pytest.raises(WorkflowError, match=r"DEGRADED:") as err:
        transition_entity(
            db,
            settings=settings,
            entity_type="lead",
            entity_id=lead.lead_id,
            to_state="attempted_contact",
            recommendation_id=None,
            reason="Proceed despite outage",
            actor_id="user-1",
            actor_role="manager",
        )

    blocked_id = str(err.value).split(":", maxsplit=1)[1]
    blocked = db.get(BlockedAction, blocked_id)
    assert blocked is not None
    assert blocked.action_type == "lead_transition"
    assert blocked.status == "queued"
    assert blocked.entity_id == lead.lead_id
