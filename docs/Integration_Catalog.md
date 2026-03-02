# Integration Catalog

- Owner: Engineering + Operations
- Version: 0.1-draft
- Last Updated: 2026-03-02

## 1. Third-Party Services

### INT-001 Messaging Provider (Twilio or equivalent)

- Purpose: outbound SMS/voice notifications for follow-ups and deadline alerts.
- Owner: Operations Engineering.
- Auth method: API key + account SID.
- Rate limit: provider-defined, enforce local queue throttling.
- SLA: provider default.
- Failure mode: queue retry with exponential backoff; fallback to email.

### INT-002 Email Provider (SendGrid or equivalent)

- Purpose: transactional notifications and report delivery.
- Owner: Platform Engineering.
- Auth method: API key.
- Rate limit: provider-defined.
- SLA: provider default.
- Failure mode: retry + dead-letter queue after max attempts.

### INT-003 E-signature Provider (DocuSign or equivalent) [Phase 2]

- Purpose: signature workflows for offer and compliance documents.
- Owner: Transaction Operations.
- Auth method: OAuth client credentials.
- Rate limit: provider-defined.
- SLA: provider default.
- Failure mode: revert to manual signature runbook.

### INT-004 Geocoding/Property Data Enrichment [Optional]

- Purpose: normalize addresses and enrich basic property metadata.
- Owner: Data Engineering.
- Auth method: API key.
- Rate limit: provider-defined.
- SLA: best effort.
- Failure mode: manual entry path remains available.

## 2. Events, Webhooks, and Callbacks

- Incoming webhooks must validate signature and timestamp.
- Webhook handler writes raw payload + normalized event record.
- Idempotency key required to prevent duplicate processing.

## 3. Data Exchange Contracts

- Contract definitions must be versioned and testable.
- PII-minimized payloads are required wherever feasible.
- Integration adapters must map provider errors to internal error codes.

## 4. Monitoring and Alerting Responsibilities

- Integration owner defines success/failure SLO and pager path.
- Alerts required for sustained 5xx or callback signature failures.
- Weekly integration health report shared with operations.
