"""Pydantic request/response schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    error: dict[str, Any]


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class AISessionCreate(BaseModel):
    entity_type: str
    entity_id: str
    context_payload: dict[str, Any] = Field(default_factory=dict)
    prompt_version: str = "v1"


class AISessionOut(BaseModel):
    session_id: str
    entity_type: str
    entity_id: str
    context_hash: str
    prompt_version: str
    created_by: str
    created_at: datetime


class AIRecommendationCreate(BaseModel):
    session_id: str
    action: str
    context_override: dict[str, Any] = Field(default_factory=dict)


class AIRecommendationOut(BaseModel):
    recommendation_id: str
    session_id: str
    action: str
    rationale: str
    confidence: float
    risk_flags: list[str]
    status: str
    model_name: str
    model_version: str
    prompt_hash: str
    approval_required: bool
    created_at: datetime


class ApprovalDecisionRequest(BaseModel):
    decision: str
    reason: str


class ApprovalGateOut(BaseModel):
    gate_id: str
    recommendation_id: str
    required_role: str
    decision: str
    decision_reason: str | None
    decided_by: str | None
    decided_at: datetime | None
    created_at: datetime


class TransitionRequest(BaseModel):
    to_state: str
    recommendation_id: str | None = None
    reason: str = ""


class LeadCreate(BaseModel):
    source: str
    name: str
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    parcel_id: str | None = None
    motivation_level: int | None = None
    pain_points: str | None = None
    timeline: str | None = None
    assigned_to: str | None = None


class LeadOut(BaseModel):
    lead_id: str
    source: str
    name: str
    status: str
    assigned_to: str | None
    created_at: datetime
    updated_at: datetime


class AnalysisCreate(BaseModel):
    lead_id: str
    arv: float | None = None
    as_is_value: float | None = None
    rehab_budget: float | None = None
    cap_rate: float | None = None
    cash_on_cash: float | None = None
    target_offer_price: float | None = None
    max_offer_price: float | None = None
    notes: str | None = None
    recommendation_id: str | None = None


class AnalysisDecisionRequest(BaseModel):
    status: str
    recommendation_id: str | None = None
    reason: str = ""


class AnalysisOut(BaseModel):
    analysis_id: str
    lead_id: str
    status: str
    target_offer_price: float | None
    max_offer_price: float | None
    created_at: datetime
    updated_at: datetime


class DealCreate(BaseModel):
    analysis_id: str | None = None
    property_address: str
    purchase_price: float | None = None
    earnest_money: float | None = None
    financing_type: str | None = None
    recommendation_id: str | None = None


class DealOut(BaseModel):
    deal_id: str
    analysis_id: str | None
    property_address: str
    stage: str
    created_at: datetime
    updated_at: datetime


class CaseCreate(BaseModel):
    linked_deal_id: str | None = None
    title: str
    case_type: str
    priority: str = "normal"
    severity: str = "functional"
    assigned_to: str | None = None
    recommendation_id: str | None = None


class CaseOut(BaseModel):
    case_id: str
    linked_deal_id: str | None
    title: str
    case_type: str
    priority: str
    severity: str
    status: str
    created_at: datetime
    updated_at: datetime


class DocumentImportRequest(BaseModel):
    entity_type: str
    entity_id: str
    file_name: str
    file_path: str
    checksum: str | None = None


class DocumentOut(BaseModel):
    document_id: str
    entity_type: str
    entity_id: str
    file_name: str
    file_path: str
    checksum: str | None
    created_by: str
    created_at: datetime


class TimelineEventOut(BaseModel):
    event_id: str
    event_type: str
    actor_type: str
    actor_id: str
    entity_type: str
    entity_id: str
    payload_json: dict[str, Any]
    created_at: datetime


class HealthOut(BaseModel):
    status: str
    ai_state: str
    blocked_actions_queued: int
