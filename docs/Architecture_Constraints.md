# Architecture Constraints

- Owner: Engineering
- Version: 0.1-draft
- Last Updated: 2026-03-02

## 1. Approved Tech Stack

- Backend: Python 3.12 + FastAPI + Pydantic v2.
- Data Access: SQLAlchemy 2 + Alembic migrations.
- Databases:
- Local/dev default: SQLite.
- Hosted default: PostgreSQL 16.
- Background jobs: Redis-backed worker queue (RQ or Celery).
- Frontend (internal MVP): Streamlit or thin web client consuming REST API.
- Test stack: `pytest`, contract tests for APIs, migration tests.
- AI orchestration layer: Gemini gateway service + prompt/version management.
- Storage/object files: local filesystem (MVP) or MinIO (self-hosted).
- Observability: Prometheus + Grafana + Loki (open-source stack).

## 2. Disallowed Technologies (MVP)

- No unversioned database schema changes.
- No direct production writes outside service APIs.
- No tight coupling to a single AI provider API in core business logic.
- No browser-only local storage as system of record.
- No paid SaaS tooling dependencies, except approved Google AI Pro usage.

## 3. Hosting and Infrastructure Constraints

- All environments must run from Infrastructure-as-Code or repeatable scripts.
- Secrets must come from environment variables or managed secret store.
- Single-command local bootstrap required for developers.

## 4. Build vs Buy Decisions

- Build in-house: core workflow/state engine, audit timeline, schema model.
- Build in-house: AI orchestration, context assembly, and approval-gate enforcement.
- Integrate free/open services only for MVP (SMTP, OSM, self-hosted tools).
- Any integration must have clear fallback path or degradation mode.

## 5. Data Residency and Regional Constraints

- Default region: United States.
- No cross-region replication for MVP unless explicitly required.
- Residency constraints must be validated before onboarding external integrations.

## 6. Operational Constraints

- All workflow transitions must be deterministic and replay-safe.
- Core workflow transitions must reference a persisted AI recommendation event.
- Time computations must be timezone-aware (`America/Los_Angeles` default for business deadlines).
- Manual overrides require reason and actor metadata.

## 7. Architectural Decision Records (ADRs)

- ADR-001: Service-first architecture with API boundary between UI and domain logic.
- ADR-002: Canonical relational data model with append-only audit timeline.
- ADR-003: Local-first dev workflow with hosted production parity where feasible.
