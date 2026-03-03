"""API error modeling and helpers."""

from __future__ import annotations

from fastapi import HTTPException

from partner_os_v2.schemas import APIErrorResponse, ErrorCode


def error_payload(code: ErrorCode, message: str, meta: dict | None = None) -> dict:
    return APIErrorResponse(error={"code": code, "message": message, "meta": meta or {}}).model_dump(mode="json")


def api_error(status_code: int, code: ErrorCode, message: str, meta: dict | None = None) -> HTTPException:
    return HTTPException(status_code=status_code, detail=error_payload(code, message, meta))


_ERROR_RESPONSES = {
    400: {
        "model": APIErrorResponse,
        "description": "Bad request",
        "content": {"application/json": {"example": error_payload(ErrorCode.VALIDATION_ERROR, "Invalid request payload")}},
    },
    401: {
        "model": APIErrorResponse,
        "description": "Unauthorized",
        "content": {
            "application/json": {"example": error_payload(ErrorCode.UNAUTHORIZED, "Missing or invalid bearer token")}
        },
    },
    403: {
        "model": APIErrorResponse,
        "description": "Forbidden",
        "content": {
            "application/json": {
                "example": error_payload(ErrorCode.FORBIDDEN, "Insufficient permissions for requested action")
            }
        },
    },
    404: {
        "model": APIErrorResponse,
        "description": "Not found",
        "content": {"application/json": {"example": error_payload(ErrorCode.ENTITY_NOT_FOUND, "Entity not found")}},
    },
    409: {
        "model": APIErrorResponse,
        "description": "Conflict",
        "content": {
            "application/json": {
                "example": error_payload(ErrorCode.RECOMMENDATION_REQUIRED, "AI recommendation is required")
            }
        },
    },
    503: {
        "model": APIErrorResponse,
        "description": "Service unavailable",
        "content": {
            "application/json": {
                "example": error_payload(
                    ErrorCode.AI_RUNTIME_UNAVAILABLE,
                    "AI runtime unavailable",
                    {"blocked_action_id": "example-id"},
                )
            }
        },
    },
}


def error_responses(*statuses: int) -> dict[int, dict]:
    return {code: _ERROR_RESPONSES[code] for code in statuses}


def workflow_http_error(message: str) -> HTTPException:
    if message.startswith("DEGRADED:"):
        blocked_id = message.split(":", maxsplit=1)[1]
        return api_error(
            503,
            ErrorCode.DEGRADED_MODE,
            "AI runtime degraded; action queued",
            {"blocked_action_id": blocked_id},
        )

    if message.startswith("Invalid transition"):
        return api_error(409, ErrorCode.INVALID_TRANSITION, message)
    if message == "Recommendation required":
        return api_error(409, ErrorCode.RECOMMENDATION_REQUIRED, message)
    if message == "Recommendation not found":
        return api_error(409, ErrorCode.RECOMMENDATION_NOT_FOUND, message)
    if message == "Recommendation rejected":
        return api_error(409, ErrorCode.RECOMMENDATION_REJECTED, message)
    if message == "Recommendation does not match target entity":
        return api_error(409, ErrorCode.RECOMMENDATION_ENTITY_MISMATCH, message)
    if message == "Approval gate required for high-risk transition":
        return api_error(409, ErrorCode.APPROVAL_REQUIRED, message)
    if message.endswith("not found"):
        return api_error(404, ErrorCode.ENTITY_NOT_FOUND, message)
    return api_error(409, ErrorCode.WORKFLOW_ERROR, message)
