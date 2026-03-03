"""Domain-level workflow transition rules."""

from __future__ import annotations

from typing import Final

LEAD_TRANSITIONS: Final[dict[str, set[str]]] = {
    "new": {"attempted_contact", "dead_archived"},
    "attempted_contact": {"connected", "nurture", "dead_archived"},
    "connected": {"qualified", "nurture", "dead_archived"},
    "nurture": {"connected", "qualified", "dead_archived"},
    "qualified": {"dead_archived"},
    "dead_archived": set(),
}

ANALYSIS_TRANSITIONS: Final[dict[str, set[str]]] = {
    "draft": {"under_review", "rejected"},
    "under_review": {"approved_for_offer", "rejected"},
    "approved_for_offer": {"archived"},
    "rejected": {"archived"},
    "archived": set(),
}

DEAL_TRANSITIONS: Final[dict[str, set[str]]] = {
    "drafting_structuring": {"negotiation", "dead"},
    "negotiation": {"mutual_acceptance", "dead"},
    "mutual_acceptance": {"due_diligence", "dead"},
    "due_diligence": {"funding_alignment", "dead"},
    "funding_alignment": {"escrow_closing", "dead"},
    "escrow_closing": {"closed", "dead"},
    "closed": {"post_close"},
    "post_close": set(),
    "dead": set(),
}

CASE_TRANSITIONS: Final[dict[str, set[str]]] = {
    "new": {"triage", "blocked"},
    "triage": {"in_progress", "blocked"},
    "in_progress": {"review", "blocked"},
    "blocked": {"in_progress", "review"},
    "review": {"resolved", "in_progress"},
    "resolved": set(),
}

HIGH_RISK_ACTIONS: Final[set[str]] = {
    "deal_close",
    "deal_mark_dead",
    "deal_waive_contingency",
    "case_resolve_critical",
}


def can_transition(entity_type: str, from_state: str, to_state: str) -> bool:
    graph = {
        "lead": LEAD_TRANSITIONS,
        "analysis": ANALYSIS_TRANSITIONS,
        "deal": DEAL_TRANSITIONS,
        "case": CASE_TRANSITIONS,
    }.get(entity_type)
    if graph is None:
        return False
    return to_state in graph.get(from_state, set())


def is_high_risk(entity_type: str, action: str, to_state: str, severity: str | None = None) -> bool:
    if action in HIGH_RISK_ACTIONS:
        return True
    if entity_type == "deal" and to_state in {"closed", "dead"}:
        return True
    if entity_type == "case" and to_state == "resolved" and (severity or "").lower() == "critical":
        return True
    return False
