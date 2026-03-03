# Data Model

- Owner: Engineering + Data
- Version: 0.1-draft
- Last Updated: 2026-03-02

## 1. Entities

- `User`: identity, role, status.
- `Lead`: intake source, contact profile, qualification status.
- `Analysis`: underwriting inputs, computed outputs, decision status.
- `Deal`: terms, deadlines, stage, compliance checklist.
- `Case`: operational work item with type/severity/status.
- `Property`: normalized property reference and attributes.
- `Document`: storage metadata, checksum, entity links.
- `ActivityLog`: immutable event stream for state changes.
- `Task`: actionable work with due date and owner.
- `AISession`: scoped context for AI interaction windows.
- `AIRecommendation`: structured recommendation, rationale, and confidence.
- `ApprovalGate`: human decision records for AI-proposed high-risk actions.

## 2. Relationships

- A `Lead` can have zero or more `Analysis` records.
- An `Analysis` can produce zero or one `Deal`.
- A `Deal` can have zero or more `Case` records.
- A `Property` can link to many leads/deals/cases.
- A `Document` can link to one or more core entities.
- Every state-changing write must emit one `ActivityLog` entry.
- Each core workflow entity can have many `AISession` records.
- Each `AISession` can emit many `AIRecommendation` records.
- Each high-risk `AIRecommendation` must link to one `ApprovalGate` record before execution.

## 3. Schema Rules and Constraints

- Primary IDs are UUIDs.
- Status/stage fields are enums with explicit transition maps.
- Financial numeric fields use fixed precision decimal types.
- Required fields enforced at API boundary and DB constraint layer.
- Soft-delete uses `archived_at` + `archived_by` metadata.
- AI records store model ID/version, prompt hash, and response token usage metadata.

## 4. Data Lifecycle

- Creation: through API commands only.
- Updates: immutable event + current-state projection model.
- Retention: records retained minimum 7 years by default policy.
- Deletion: hard delete blocked except controlled admin maintenance flows.

## 5. Migration Strategy

- Schema migrations are forward-only and versioned with Alembic.
- Every migration includes rollback notes and data safety checks.
- Zero-downtime migration path required for hosted environments.

## 6. Backup and Restore Expectations

- Local mode: automated daily snapshot + manual export command.
- Hosted mode: point-in-time recovery where supported.
- Quarterly restore drill required with documented recovery timings.
