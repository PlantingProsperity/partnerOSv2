# User Flows

- Owner: Product + Engineering
- Version: 0.1-draft
- Last Updated: 2026-03-02

## 1. Actors

- Acquisition Manager
- Underwriter
- Transaction Coordinator
- Operations Manager
- Principal/Partner
- AI Partner
- System Agent (automations only)

## 2. Core Flows

### 2.1 Lead Intake and Qualification

- Trigger: New inbound lead from call, referral, form, or manual entry.
- Preconditions: User has `create_lead` permission.
- Main Steps:
1. Create lead record with source and contact information.
2. Add motivation/timeline notes and schedule follow-up.
3. Move lead status through `New -> Attempted Contact -> Connected`.
4. Mark as `Qualified` when ready for underwriting.
- Postconditions: Lead has owner, next action date, and current status.

### 2.2 Underwriting Analysis

- Trigger: Lead marked `Qualified`.
- Preconditions: Property context exists (address or parcel).
- Main Steps:
1. Create analysis linked to lead.
2. Enter valuation, rehab, rent, and timeline inputs.
3. Compute core outputs (cap rate, cash-on-cash, max offer range).
4. Mark analysis as `Approved_for_Offer` or `Rejected`.
- Postconditions: Decision-ready analysis artifact with rationale.

### 2.3 Deal Creation and Execution

- Trigger: Analysis approved for offer.
- Preconditions: Analysis status is `Approved_for_Offer`.
- Main Steps:
1. Create deal and copy forward relevant analysis values.
2. Set deal stage to `Drafting/Structuring`.
3. Track deadlines from `mutual_acceptance_date` once available.
4. Progress through negotiation, due diligence, funding, closing.
- Postconditions: Deal reaches `Closed` or `Dead` with full audit history.

### 2.4 Operations Case Management

- Trigger: Non-deal operational request raised (maintenance, vendor, finance).
- Preconditions: User has `create_case` permission.
- Main Steps:
1. Create case with type, severity, due date, and owner.
2. Move through `New -> Triage -> In_Progress`.
3. Capture vendor actions, approvals, and costs.
4. Complete review and mark `Resolved`.
- Postconditions: Case is resolved with full interaction log.

### 2.5 Document Ingestion and Linking

- Trigger: File uploaded, imported, or generated.
- Preconditions: Target entity exists.
- Main Steps:
1. Assign normalized filename and metadata.
2. Link document to lead/analysis/deal/case.
3. Update checklist status for required documents.
4. Record ingestion event in timeline.
- Postconditions: Document discoverable by entity and checklist state.

### 2.6 AI Partner Orchestration Loop

- Trigger: User initiates or system requires a workflow decision.
- Preconditions: Authenticated session and linked entity context exists.
- Main Steps:
1. System sends normalized context packet to AI partner.
2. AI returns recommendation, rationale, and confidence signal.
3. User accepts, edits, or rejects recommendation.
4. System records AI output + final human decision in timeline.
- Postconditions: AI interaction is traceable and linked to resulting action.

## 3. Alternate Flows

- Lead can move to `Nurture` with recurring follow-up reminders.
- Analysis may require additional comps and remain `Under_Review`.
- Deal can regress to prior stage if contingencies fail.
- Case can transition to `Blocked` pending external dependency.

## 4. Error Flows

- Missing required fields block state transitions.
- Unauthorized role attempts action; API returns permission error.
- Deadline compute failure triggers validation error and alert.
- Document ingestion failure moves item to retry queue with reason code.

## 5. Edge Cases

- Duplicate lead detection with merge workflow.
- Multiple properties tied to one seller/contact.
- Deal split across multiple buyer entities.
- Emergency case creation outside normal business hours.

## 6. UX Notes and Constraints

- Every state transition requires optional notes and explicit confirmation.
- Core workflow actions require an AI recommendation trace plus human confirmation for high-risk steps.
- High-risk actions (close deal, waive contingency, mark case resolved) require elevated role confirmation.
- Timeline view must show actor, action, timestamp, and rationale in one screen.
