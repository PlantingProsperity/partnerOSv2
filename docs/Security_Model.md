# Security Model

- Owner: Security + Engineering
- Version: 0.1-draft
- Last Updated: 2026-03-02

## 1. Threat Model Scope

- Unauthorized access to operational and financial data.
- Privilege escalation through weak role boundaries.
- Data tampering of status transitions or audit records.
- Secret leakage through logs, code, or environment misconfiguration.
- Third-party webhook spoofing.

## 2. Authentication

- User authentication via managed identity provider or secure local auth for MVP.
- Passwordless or MFA-capable path required for privileged roles.
- Session expiration and token rotation enforced.

## 3. Authorization

- Policy model: RBAC with least-privilege defaults.
- Write operations require explicit permission checks.
- Sensitive state transitions require elevated role confirmation.

## 4. Roles and Permissions Matrix

- `Admin`: full system and configuration control.
- `Manager`: approve transitions, assign work, view all entities.
- `Underwriter`: create/update analyses, view leads/deals.
- `Acquisition`: manage leads and related activities.
- `Ops`: manage cases and operational documents.
- `ReadOnly`: view-only access for audit/reporting.

## 5. Secrets Management

- Local: `.env` for development only, never committed.
- Hosted: managed secret store with rotation schedule.
- Secrets masked in logs and excluded from trace payloads.

## 6. Audit Logging

- Immutable append-only events for auth, transition, and admin actions.
- Audit entries include actor, action, target, timestamp, and reason.
- Audit data is exportable for compliance review.

## 7. Incident Response Requirements

- Severity rubric (SEV-1 to SEV-4) with owner-on-call mapping.
- Initial incident acknowledgement within 15 minutes for SEV-1/SEV-2.
- Post-incident report required within 5 business days for SEV-1/SEV-2.

## 8. Security Testing Requirements

- SAST on every merge to main.
- Dependency vulnerability scan at least weekly.
- Targeted authorization tests for all write endpoints.
- Annual penetration test before external multi-tenant rollout.
