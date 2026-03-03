# API Contracts

- Owner: Engineering
- Version: 0.1-draft
- Last Updated: 2026-03-02

## 1. API Inventory

- Internal domain API: Partner_OS_v2 service (`/api/v1`).
- Internal admin API: operational diagnostics and maintenance endpoints.
- External APIs (planned): Google Gemini (core), messaging provider, e-signature provider, enrichment/geocoding.

## 2. Protocols and Formats

- Protocol: HTTPS REST (JSON).
- Content type: `application/json`.
- Time format: ISO 8601 UTC for persistence; localized in UI.
- Pagination: cursor-based for timeline and large list endpoints.

## 3. Authentication and Authorization

- Auth: Bearer JWT access token with short TTL + refresh token flow.
- Service-to-service auth: mTLS or signed service tokens.
- Authorization: role and permission checks on every write endpoint.

## 4. Endpoints and Schemas

### Core Endpoints (MVP)

- `POST /api/v1/leads`
- `PATCH /api/v1/leads/{lead_id}`
- `POST /api/v1/leads/{lead_id}/transitions`
- `POST /api/v1/analyses`
- `POST /api/v1/analyses/{analysis_id}/decision`
- `POST /api/v1/deals`
- `POST /api/v1/deals/{deal_id}/stages`
- `POST /api/v1/cases`
- `POST /api/v1/cases/{case_id}/transitions`
- `POST /api/v1/documents/import`
- `GET /api/v1/timeline`
- `POST /api/v1/ai/sessions`
- `POST /api/v1/ai/recommendations`
- `POST /api/v1/ai/recommendations/{recommendation_id}/approve`
- `GET /api/v1/ai/sessions/{session_id}`

Schema source of truth to be published as OpenAPI at `/openapi.json`.

## 5. Error Model

All error responses include:

- `error.code` (stable, machine-readable)
- `error.message` (human-readable)
- `error.details` (field/context list)
- `request_id`

HTTP status mapping:

- `400` validation
- `401` unauthenticated
- `403` unauthorized
- `404` not found
- `409` conflict/invalid transition
- `429` rate limit
- `500` internal

## 6. Versioning and Deprecation Policy

- API namespace uses major version path (`/api/v1`).
- Backward-compatible fields may be added without version bump.
- Breaking changes require new major version and migration window >= 90 days.

## 7. Rate Limits and Timeouts

- Internal UI token: 600 requests/minute.
- Service integration token: 120 requests/minute.
- AI recommendation endpoint target: 60 requests/minute per authenticated user.
- Default request timeout: 15 seconds.
- Long-running jobs return asynchronous job IDs.
