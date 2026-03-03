"""AI gateway service for recommendation generation."""

from __future__ import annotations

import json
from hashlib import sha256
from typing import Any

import requests
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from partner_os_v2.config import Settings
from partner_os_v2.models import AISession, BlockedAction, SystemState
from partner_os_v2.prompts.registry import prompt_hash, render_prompt


class AIRuntimeUnavailable(RuntimeError):
    """Raised when AI recommendation generation is unavailable."""


class AIResponseError(RuntimeError):
    """Raised when AI returned an invalid response payload."""


def get_ai_state(db: Session) -> str:
    state = db.get(SystemState, "ai_state")
    if state is None:
        state = SystemState(state_key="ai_state", state_value="normal")
        db.add(state)
        db.flush()
    return state.state_value


def set_ai_state(db: Session, value: str) -> None:
    state = db.get(SystemState, "ai_state")
    if state is None:
        state = SystemState(state_key="ai_state", state_value=value)
        db.add(state)
    else:
        state.state_value = value


def queue_blocked_action(
    db: Session,
    *,
    action_type: str,
    entity_type: str,
    entity_id: str,
    payload_json: dict[str, Any],
    reason: str,
    created_by: str,
) -> BlockedAction:
    blocked = BlockedAction(
        action_type=action_type,
        entity_type=entity_type,
        entity_id=entity_id,
        payload_json=payload_json,
        reason=reason,
        created_by=created_by,
    )
    db.add(blocked)
    db.flush()
    return blocked


def blocked_count(db: Session) -> int:
    return int(db.scalar(select(func.count()).select_from(BlockedAction).where(BlockedAction.status == "queued")) or 0)


class GeminiGateway:
    """Gemini recommendation generator with mock-mode support."""

    def __init__(self, settings: Settings):
        self.settings = settings

    @property
    def endpoint(self) -> str:
        return (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.settings.gemini_model}:generateContent"
        )

    def generate(
        self,
        *,
        ai_session: AISession,
        action: str,
        context_payload: dict[str, Any],
    ) -> dict[str, Any]:
        prompt = render_prompt(ai_session.prompt_version, action, context_payload)
        p_hash = prompt_hash(prompt)

        if self.settings.ai_mode == "mock":
            return {
                "action": action,
                "rationale": "Mock AI recommendation generated for local workflow testing.",
                "confidence": 0.82,
                "risk_flags": [],
                "model_name": "mock-gemini",
                "model_version": "v0",
                "prompt_hash": p_hash,
                "raw_output": {"mode": "mock"},
            }

        if not self.settings.gemini_api_key:
            raise AIRuntimeUnavailable("GEMINI API key not configured")

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "response_mime_type": "application/json",
            },
        }
        params = {"key": self.settings.gemini_api_key}
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(
                self.endpoint,
                headers=headers,
                params=params,
                json=payload,
                timeout=self.settings.gemini_timeout_seconds,
            )
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            raise AIRuntimeUnavailable(str(exc)) from exc

        parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
        text = "\n".join(part.get("text", "") for part in parts).strip()
        if not text:
            raise AIResponseError("Gemini returned empty recommendation payload")

        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            parsed = {
                "action": action,
                "rationale": text,
                "confidence": 0.50,
                "risk_flags": ["response_parse_warning"],
            }

        if "action" not in parsed or "rationale" not in parsed or "confidence" not in parsed:
            raise AIResponseError("Recommendation payload missing required keys")

        return {
            "action": str(parsed.get("action", action)),
            "rationale": str(parsed.get("rationale", "")),
            "confidence": float(parsed.get("confidence", 0.5)),
            "risk_flags": [str(x) for x in parsed.get("risk_flags", [])],
            "model_name": self.settings.gemini_model,
            "model_version": "v1",
            "prompt_hash": p_hash,
            "raw_output": data,
        }


def hash_context(context_payload: dict[str, Any]) -> str:
    serialized = json.dumps(context_payload, sort_keys=True)
    return sha256(serialized.encode("utf-8")).hexdigest()
