# Partner_OS_v2 Implementation Plan

- Owner: Engineering
- Version: 1.0
- Last Updated: 2026-03-02

## 1. Summary

This plan delivers an AI-first, local-first MVP for Partner_OS_v2 using free/open-source tooling only, with Google AI Pro (Gemini) as the sole paid exception.

The MVP must enforce:

- AI recommendation linkage for core workflow actions.
- Human approval gates for irreversible/high-risk actions.
- Degraded-mode handling (queue + admin emergency override) when AI runtime is unavailable.

## 2. Locked Decisions

- Deployment: Local-first only.
- Scope: Single-team MVP.
- AI runtime: Gemini API key path.
- Compliance target: Washington state first.
- Auth: Local auth + RBAC.
- AI outage policy: Queue + admin emergency override.
- Operator UI: Streamlit internal console.
- Alerts: In-app alerts + SMTP email.
- Codebase strategy: Greenfield V2.

## 3. Target Architecture

### 3.1 Application Stack

- Backend: FastAPI + SQLAlchemy + Alembic.
- Database: SQLite for MVP, schema-compatible with PostgreSQL.
- AI layer: Gemini gateway with prompt/version management.
- UI: Streamlit consuming REST APIs only.
- Background processing: queue worker for retries and alerts.
- Observability: structured logs + AI latency/failure metrics.

### 3.2 Core Domain Objects

- `Lead`
- `Analysis`
- `Deal`
- `Case`
- `AISession`
- `AIRecommendation`
- `ApprovalGate`
- `AuditEvent`
- `BlockedAction`
- `Alert`

## 4. Public API Surface (MVP)

- `POST /api/v1/auth/login`
- `POST /api/v1/ai/sessions`
- `POST /api/v1/ai/recommendations`
- `POST /api/v1/ai/recommendations/{recommendation_id}/approve`
- `GET /api/v1/ai/sessions/{session_id}`
- `POST /api/v1/leads`
- `POST /api/v1/leads/{lead_id}/transitions`
- `POST /api/v1/analyses`
- `POST /api/v1/deals`
- `POST /api/v1/deals/{deal_id}/stages`
- `POST /api/v1/cases`
- `POST /api/v1/cases/{case_id}/transitions`
- `POST /api/v1/documents/import`
- `GET /api/v1/timeline`
- `GET /api/v1/health`

## 5. Enforcement Rules

### 5.1 AI-First Rules

- Core transitions require a persisted `AIRecommendation` ID.
- Recommendation record must include action, rationale, confidence, risk flags, prompt hash, and model metadata.
- Recommendation and resulting action must be linked in the audit timeline.

### 5.2 Approval-Gate Rules

- High-risk actions require `ApprovalGate` decision by authorized role before execution.
- High-risk examples:
- Deal close.
- Deal death/termination.
- Waive critical contingencies.
- Critical-case resolution.

### 5.3 Degraded-Mode Rules

- On AI runtime failure:
- System sets degraded flag.
- Action request is queued as `BlockedAction`.
- API returns explicit degraded-mode response.
- Admin emergency override may generate a synthetic approved recommendation with full audit trail.

## 6. Data and Migration Plan

- Establish Alembic baseline migration with all MVP tables.
- Add explicit indexes for status/stage and timeline query paths.
- Enforce foreign keys and uniqueness on recommendation->approval linkage.
- Require all state transitions to emit append-only audit events.

## 7. Delivery Phases

### Phase 0: Project Bootstrap

- Initialize Python package, settings, database, migration scaffolding, and test harness.
- Exit criteria: app boots, health endpoint returns, migration applies on clean DB.

### Phase 1: AI Contract Core

- Implement AI session/recommendation entities and Gemini gateway.
- Add prompt registry with versioning and response schema validation.
- Exit criteria: recommendation path persists structured output + audit event.

### Phase 2: Workflow and Gate Engine

- Implement deterministic transition maps for Lead/Analysis/Deal/Case.
- Enforce recommendation linkage and approval-gate checks.
- Exit criteria: invalid transitions and missing recommendation IDs are rejected with deterministic errors.

### Phase 3: API Surface and Auth

- Implement token auth, RBAC middleware, and entity routes.
- Publish OpenAPI and stable error model.
- Exit criteria: contract tests green for auth, permissions, transitions, and failures.

### Phase 4: Operator Console

- Build Streamlit views for entities, AI recommendations, approvals, and timeline.
- Add degraded-mode banner and blocked-action queue visibility.
- Exit criteria: internal operators can complete end-to-end workflow through UI.

### Phase 5: Alerts and Retry Jobs

- Add in-app alert generation and SMTP delivery with retries/backoff.
- Exit criteria: overdue/degraded events trigger in-app + email notifications.

### Phase 6: Hardening and Pilot Readiness

- Add metrics, resilience tests, security checks, and runbooks.
- Exit criteria: pilot checklist and acceptance tests complete.

## 8. Test Plan

### 8.1 Golden Scenarios

- Lead intake -> AI recommendation -> qualification transition.
- Analysis recommendation -> approved offer decision -> deal creation.
- High-risk deal transition blocked until approval gate passes.
- AI outage queues action, admin override unlocks transition.

### 8.2 Failure Scenarios

- Gemini timeout/unavailable returns degraded-mode error and queue entry.
- Missing recommendation ID returns `409`.
- Unauthorized approval attempt returns `403` and denied audit event.
- Duplicate transition request is idempotent.

### 8.3 Non-Functional Tests

- AI recommendation p95 latency checks.
- Queue retry/dead-letter behavior checks.
- Audit completeness: every state-changing action has linked audit event.

## 9. Acceptance Criteria

MVP is accepted when:

- AI-first workflow gates are technically enforced.
- High-risk actions require and persist human approval decisions.
- Degraded mode is explicit, auditable, and operationally safe.
- Core API and Streamlit console support daily operator workflows.
- Test suite passes for golden, failure, RBAC, and outage scenarios.

## 10. Commit Strategy

1. `chore: bootstrap v2 project skeleton and tooling`
2. `feat: add AI session recommendation approval domain models`
3. `feat: implement gemini gateway and prompt registry`
4. `feat: enforce workflow transition engine and approval gates`
5. `feat: expose auth ai workflow and timeline APIs`
6. `feat: add streamlit operator console`
7. `feat: add alerts retry and degraded-mode queue handling`
8. `test: add golden failure and permission suites`
9. `docs: add runbooks and operational checklists`
