from __future__ import annotations

from partner_os_v2.api.main import app


def test_openapi_contains_required_ai_first_paths():
    spec = app.openapi()
    paths = spec.get("paths", {})

    required = {
        "/api/v1/auth/login": {"post"},
        "/api/v1/ai/sessions": {"post"},
        "/api/v1/ai/recommendations": {"post"},
        "/api/v1/ai/recommendations/{recommendation_id}/approve": {"post"},
        "/api/v1/leads": {"post"},
        "/api/v1/leads/{lead_id}/transitions": {"post"},
        "/api/v1/analyses": {"post"},
        "/api/v1/analyses/{analysis_id}/decision": {"post"},
        "/api/v1/deals": {"post"},
        "/api/v1/deals/{deal_id}/stages": {"post"},
        "/api/v1/cases": {"post"},
        "/api/v1/cases/{case_id}/transitions": {"post"},
        "/api/v1/documents/import": {"post"},
        "/api/v1/timeline": {"get"},
        "/api/v1/health": {"get"},
    }

    for path, methods in required.items():
        assert path in paths, f"Missing path: {path}"
        assert methods.issubset(set(paths[path].keys())), f"Missing methods for {path}"


def test_openapi_has_ai_schema_shapes():
    spec = app.openapi()
    components = spec.get("components", {}).get("schemas", {})

    assert "AIRecommendationOut" in components
    assert "AISessionOut" in components
    assert "ApprovalGateOut" in components

    ai_props = components["AIRecommendationOut"].get("properties", {})
    for required_prop in ["recommendation_id", "action", "rationale", "confidence", "approval_required"]:
        assert required_prop in ai_props


def test_openapi_has_error_code_enum_and_examples():
    spec = app.openapi()
    components = spec.get("components", {}).get("schemas", {})
    assert "ErrorCode" in components
    enum_values = set(components["ErrorCode"].get("enum", []))
    for required in {"unauthorized", "forbidden", "recommendation_required", "ai_runtime_unavailable"}:
        assert required in enum_values

    lead_transition = spec["paths"]["/api/v1/leads/{lead_id}/transitions"]["post"]
    responses = lead_transition.get("responses", {})
    assert "409" in responses
    assert "503" in responses

    ai_recommendation = spec["paths"]["/api/v1/ai/recommendations"]["post"]
    request_body = ai_recommendation.get("requestBody", {}).get("content", {}).get("application/json", {})
    assert "examples" in request_body
