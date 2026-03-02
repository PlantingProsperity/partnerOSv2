# Partner_OS_v2 Planning Docs

This folder holds the baseline technical documentation for planning and building Partner_OS_v2.

## Program Context

Partner_OS_v2 is an internal operating platform for real-estate investment/brokerage operations. It unifies lead intake, underwriting, deal execution, and operational casework while preserving auditability and compliance.

## Working Assumptions (Initial Draft)

- Deployment model is local-first for early releases, with optional cloud-hosted environments later.
- Primary users are internal team members (not public customers).
- Data model centers on `Lead -> Analysis -> Deal -> Case` with shared document and activity logs.
- AI is advisory/assistive and must never bypass explicit human approval checkpoints.

## Document Set

1. `PRD.md` - product outcomes, scope, and feature priorities.
2. `User_Flows.md` - end-to-end workflows, edge cases, and failure paths.
3. `Requirements_Spec.md` - functional requirements and acceptance criteria.
4. `NFRs.md` - performance, reliability, security, observability, and cost constraints.
5. `Architecture_Constraints.md` - stack decisions and engineering boundaries.
6. `API_Contracts.md` - service interfaces, schemas, auth, and error model.
7. `Data_Model.md` - entities, relationships, lifecycle, and migration strategy.
8. `Integration_Catalog.md` - third-party dependencies and ownership.
9. `Security_Model.md` - threat model, controls, and incident expectations.
10. `Delivery_Constraints.md` - schedule, capacity, environments, release protocol.

## Exit Criteria To Start Build Planning

- All open questions in `PRD.md` are resolved or explicitly deferred.
- `Requirements_Spec.md` and `User_Flows.md` are traceable to each other.
- `Architecture_Constraints.md` and `NFRs.md` have no critical conflicts.
- Security and integration owners are assigned.
