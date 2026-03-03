# Integration Catalog

- Owner: Engineering + Operations
- Version: 0.1-draft
- Last Updated: 2026-03-02

## 1. Third-Party Services

### INT-001 Email Delivery (SMTP)

- Purpose: transactional notifications and report delivery.
- Owner: Operations Engineering.
- Auth method: SMTP credentials (app password or service account).
- Rate limit: provider-defined, enforce local queue throttling.
- SLA: provider default.
- Failure mode: queue retry with exponential backoff; fallback to in-app alerts.

### INT-002 Mapping/Geocoding (OpenStreetMap Nominatim or equivalent free source)

- Purpose: normalize addresses and enrich basic property metadata.
- Owner: Data Engineering.
- Auth method: API key.
- Rate limit: provider-defined.
- SLA: best effort.
- Failure mode: manual entry path remains available.

### INT-003 E-signature Workflow [Manual or Self-Hosted, Phase 2]

- Purpose: signature workflows for offer and compliance documents.
- Owner: Transaction Operations.
- Auth method: local/manual flow in MVP; self-hosted option in later phase.
- Rate limit: n/a for manual flow.
- SLA: internal operational process.
- Failure mode: revert to manual signature runbook.

### INT-004 AI Core Partner (Google Gemini via existing Google AI Pro subscription)

- Purpose: core reasoning, recommendation generation, and decision support across all primary workflows.
- Owner: Platform Engineering.
- Auth method: approved Google account / configured API key when available.
- Rate limit: subscription or provider limits.
- SLA: provider default.
- Failure mode: enter degraded mode, queue AI-required actions, and require explicit human override workflow for continuity.

## 2. Events, Webhooks, and Callbacks

- Incoming webhooks must validate signature and timestamp.
- Webhook handler writes raw payload + normalized event record.
- Idempotency key required to prevent duplicate processing.

## 3. Data Exchange Contracts

- Contract definitions must be versioned and testable.
- PII-minimized payloads are required wherever feasible.
- Integration adapters must map provider errors to internal error codes.
- Paid APIs are disallowed for MVP unless explicitly approved in writing.

## 4. Monitoring and Alerting Responsibilities

- Integration owner defines success/failure SLO and pager path.
- Alerts required for sustained 5xx or callback signature failures.
- Weekly integration health report shared with operations.
