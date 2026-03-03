"""Prompt registry and render helpers."""

from __future__ import annotations

import json
from hashlib import sha256
from typing import Any

PROMPTS = {
    "v1": {
        "system": (
            "You are the AI partner for a real-estate operations system. "
            "Respond with strict JSON containing keys: action, rationale, confidence, risk_flags."
        )
    }
}


def render_prompt(version: str, action: str, context_payload: dict[str, Any]) -> str:
    template = PROMPTS.get(version) or PROMPTS["v1"]
    payload = {
        "system": template["system"],
        "action": action,
        "context": context_payload,
    }
    return json.dumps(payload, sort_keys=True)


def prompt_hash(prompt: str) -> str:
    return sha256(prompt.encode("utf-8")).hexdigest()
