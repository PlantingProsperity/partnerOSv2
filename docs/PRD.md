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

- Establish the AI partner as the primary operating interface for core decision workflows.
- Standardize lifecycle from intake to close with explicit state transitions.
- Reduce manual status-tracking and duplicate data entry.
- Preserve immutable activity history for compliance and post-mortem analysis.
- Increase decision velocity while keeping human approvals for high-risk actions.

## 4. Non-Goals

- Public consumer-facing portal in MVP.
- Full accounting/ERP replacement in MVP.
- Fully autonomous deal execution without human approval.
- Nationwide legal/regulatory automation in MVP (focus on one market first).
- Introducing paid SaaS/tooling dependencies in MVP, except approved use of Google AI Pro.

## 5. Feature Priorities

### P0 (MVP)

- AI partner conversation and recommendation loop for lead, analysis, deal, and case actions.
- Unified records for Lead, Analysis, Deal, and Case.
- Role-based workflow actions and state transitions.
- Document indexing and linkage to records.
- Activity timeline with actor, reason, and timestamp.
- Deadline tracking and alerting for critical deal milestones.
- Internal API + operator UI for daily workflow execution.

### P1 (Post-MVP)

- Advanced AI automations (batch review, proactive risk watchlists).
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
- >= 95% of qualified workflow actions include an AI recommendation event.

## 7. Risks and Assumptions

- Risk: overly broad scope slows MVP delivery.
- Risk: integration dependencies (e-signature, messaging) can delay timeline.
- Risk: Gemini access path or quota limits can bottleneck peak usage windows.
- Assumption: initial user group accepts structured workflow discipline.
- Assumption: local-first architecture remains acceptable for first release.
- Assumption: free/open-source alternatives are sufficient for required workflows.

## 8. Open Questions

- Should MVP target single-team or multi-team support on day one?
- Is cloud-hosted production required for MVP, or is local deployment acceptable?
- What is the approved Gemini runtime path under the Google AI Pro constraint?
- What legal/compliance artifacts are strictly required by jurisdiction for launch?
