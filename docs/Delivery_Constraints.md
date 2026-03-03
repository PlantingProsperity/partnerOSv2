# Delivery Constraints

- Owner: Product + Engineering
- Version: 0.1-draft
- Last Updated: 2026-03-02

## 1. Timeline and Milestones

- Milestone 0 (2026-03-09 to 2026-03-20): architecture baseline, repo scaffolding, schema contracts, AI gateway proof-of-concept.
- Milestone 1 (2026-03-23 to 2026-04-24): core Lead/Analysis/Deal/Case APIs + internal UI + AI recommendation loop.
- Milestone 2 (2026-04-27 to 2026-05-22): document flow, alerts, AI auditability, degraded-mode hardening.
- Milestone 3 (2026-05-25 to 2026-06-12): pilot rollout, bug fixes, operational readiness.

## 2. Team Capacity and Roles

- 1 Technical Lead (architecture, reviews, release governance).
- 2 Full-Stack Engineers (API/UI/workflow implementation).
- 1 QA/Automation Engineer (test strategy and release validation).
- 1 Product/Operations Owner (requirements, acceptance, rollout coordination).

## 3. Environment Strategy

- Local: single-command bootstrap, seeded sample data, fast iteration.
- Staging: production-like configuration, integration sandbox endpoints.
- Production: controlled rollout with backup and rollback runbooks.

## 4. Release Process

- Trunk-based development with protected `main` branch.
- Pull request required with automated tests and peer review.
- Weekly release train to staging; production release by checklist approval.

## 5. Rollback and Recovery Expectations

- Every release has documented rollback procedure.
- Migrations must define safe rollback or mitigation strategy.
- Recovery objective targets:
- RTO <= 2 hours.
- RPO <= 24 hours (local) or <= 15 minutes (hosted).

## 6. Definition of Done

- Feature requirements implemented and linked to acceptance criteria.
- Unit/integration tests added and passing.
- Security and permission checks validated.
- Observability hooks (logs/metrics) included.
- AI recommendation and approval-gate behavior validated with tests.
- Documentation updated in `docs/`.

## 7. Dependencies and Blockers

- Final decision on deployment model for MVP (local-only vs hosted).
- Selection of auth provider and integration stack.
- Confirmed legal/compliance checklist per target market.
- Availability of production-like test data sets.
- Confirmation that MVP will use free/open-source tooling only (except Google AI Pro).
- Confirmed Gemini runtime access method and quota envelope under Google AI Pro constraints.
