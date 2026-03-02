# Product Requirements Document (PRD)

- Owner: Founding Team (TBD)
- Version: 0.1-draft
- Last Updated: 2026-03-02

## 1. Problem Statement

The current operating workflow is fragmented across chat threads, ad-hoc scripts, and manually managed files. This creates avoidable cycle time, inconsistent execution quality, and weak visibility into operational risk.

Partner_OS_v2 will provide a single internal system for intake, underwriting, deal progression, operations, and audit history so teams can execute faster with fewer coordination failures.

## 2. Target Users and Personas

- Acquisition Manager: captures and qualifies incoming opportunities.
- Underwriter: runs financial feasibility and recommendation outputs.
- Transaction Coordinator: manages contracts, deadlines, and compliance artifacts.
- Operations Manager: runs non-deal casework (maintenance, vendor, finance ops).
- Principal/Partner: monitors pipeline health, risk, and decision approvals.

## 3. Goals

- Standardize lifecycle from intake to close with explicit state transitions.
- Reduce manual status-tracking and duplicate data entry.
- Preserve immutable activity history for compliance and post-mortem analysis.
- Increase decision velocity while keeping human approvals for high-risk actions.

## 4. Non-Goals

- Public consumer-facing portal in MVP.
- Full accounting/ERP replacement in MVP.
- Fully autonomous deal execution without human approval.
- Nationwide legal/regulatory automation in MVP (focus on one market first).

## 5. Feature Priorities

### P0 (MVP)

- Unified records for Lead, Analysis, Deal, and Case.
- Role-based workflow actions and state transitions.
- Document indexing and linkage to records.
- Activity timeline with actor, reason, and timestamp.
- Deadline tracking and alerting for critical deal milestones.
- Internal API + operator UI for daily workflow execution.

### P1 (Post-MVP)

- AI-assisted draft generation for notes, summaries, and document checklists.
- Integration connectors for messaging and e-signature.
- Advanced reporting (pipeline conversion, stage latency, SLA performance).

### P2 (Later)

- Multi-market regulatory packs.
- Predictive risk scoring based on historical outcomes.
- Multi-tenant architecture for external firm onboarding.

## 6. Success Metrics

- Lead-to-analysis cycle time reduced by >= 30% from baseline.
- Analysis-to-offer cycle time reduced by >= 25% from baseline.
- Missed critical deal deadline rate < 2% per quarter.
- 100% of deal state transitions include actor + rationale audit entries.
- Weekly active usage by >= 90% of assigned internal operators.

## 7. Risks and Assumptions

- Risk: overly broad scope slows MVP delivery.
- Risk: integration dependencies (e-signature, messaging) can delay timeline.
- Assumption: initial user group accepts structured workflow discipline.
- Assumption: local-first architecture remains acceptable for first release.

## 8. Open Questions

- Should MVP target single-team or multi-team support on day one?
- Is cloud-hosted production required for MVP, or is local deployment acceptable?
- Which external integration is mandatory in MVP: messaging, e-signature, or neither?
- What legal/compliance artifacts are strictly required by jurisdiction for launch?
