# Functional Requirements Specification

- Owner: Engineering
- Version: 0.1-draft
- Last Updated: 2026-03-02

## 1. Scope

This specification covers MVP functional behavior for AI-driven lead intake, underwriting analysis, deal management, case management, document linkage, timeline logging, and permissions.

## 2. Functional Requirements

- FR-001: System shall create, read, update, and archive Lead records.
- FR-002: System shall enforce lead status lifecycle transitions.
- FR-003: System shall create Analysis records linked to a Lead.
- FR-004: System shall compute underwriting metrics from validated numeric inputs.
- FR-005: System shall require explicit decision status for each Analysis.
- FR-006: System shall create Deal records from approved Analyses.
- FR-007: System shall enforce deal stage transitions with validation gates.
- FR-008: System shall compute and track critical deadline dates.
- FR-009: System shall create and manage operational Cases by type/severity.
- FR-010: System shall support assignment and reassignment of Leads/Deals/Cases.
- FR-011: System shall store and link Documents to any core entity.
- FR-012: System shall track required-document checklist status for Deals.
- FR-013: System shall record immutable activity logs for all state-changing actions.
- FR-014: System shall provide timeline views filtered by entity and date range.
- FR-015: System shall enforce role-based access control for write actions.
- FR-016: System shall expose versioned REST APIs for all core entities.
- FR-017: System shall support bulk export of filtered operational reports.
- FR-018: System shall flag overdue tasks/deadlines and surface alerts.
- FR-019: System shall support soft-delete/archive with restore controls for authorized users.
- FR-020: System shall persist actor-provided rationale for manual overrides.
- FR-021: System shall create and persist AI interaction sessions linked to workflow entities.
- FR-022: System shall require AI recommendation events for core workflow actions before transition execution.
- FR-023: System shall require human approval for irreversible or high-risk actions, storing both AI rationale and human decision.
- FR-024: System shall enter explicit degraded mode on AI runtime unavailability and queue/retry AI-required actions.

## 3. Acceptance Criteria

- AC-001: Creating a lead without required identity/contact fields returns validation error.
- AC-002: Invalid lifecycle transition returns deterministic error code and message.
- AC-003: Analysis computations are reproducible from stored input fields.
- AC-004: Deal cannot enter negotiation stage without minimum required documents.
- AC-005: Deadline fields are auto-populated when trigger dates become available.
- AC-006: Unauthorized action attempts return `403` and create a denied audit event.
- AC-007: Every stage/status transition creates an immutable timeline record.
- AC-008: Archived records are hidden by default but retrievable by privileged users.
- AC-009: Document linked to entity is queryable from both document and entity endpoints.
- AC-010: Overdue alert appears within one minute of threshold breach.
- AC-011: Core transition endpoints reject requests without linked AI recommendation IDs.
- AC-012: High-risk actions persist AI rationale + human approver in one atomic audit event.
- AC-013: AI session artifacts are queryable by entity and time range.
- AC-014: During AI outage, blocked actions return explicit degraded-mode response code and user guidance.

## 4. Traceability

- Lead flow maps to FR-001, FR-002, FR-010, FR-015.
- Analysis flow maps to FR-003, FR-004, FR-005.
- Deal flow maps to FR-006, FR-007, FR-008, FR-012, FR-018.
- Case flow maps to FR-009, FR-010, FR-013.
- Document flow maps to FR-011, FR-012, FR-014.
- AI flow maps to FR-021, FR-022, FR-023, FR-024.
