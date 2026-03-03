# Non-Functional Requirements (NFRs)

- Owner: Engineering + Operations
- Version: 0.1-draft
- Last Updated: 2026-03-02

## 1. Performance

- API p95 latency:
- `GET` list/detail endpoints <= 300 ms under nominal load.
- `POST/PATCH` state transition endpoints <= 800 ms under nominal load.
- Underwriting compute request <= 2 seconds for standard payload sizes.
- AI recommendation round-trip p95 <= 8 seconds for standard context payloads.
- UI first meaningful paint <= 2.5 seconds on corporate laptop baseline.

## 2. Reliability and Availability

- Target availability (hosted env): 99.5% monthly.
- AI recommendation service availability target: 99.0% monthly.
- Local deployment target: recoverable operation after process restart with zero data loss in committed transactions.
- Background jobs are retry-safe and idempotent.
- Error budget: <= 3.6 hours unavailability per month for hosted env.
- During AI outage, user-facing degraded mode must be explicit and auditable.

## 3. Scalability

- Support at least:
- 50 concurrent internal users.
- 1000 active leads.
- 500 active deals.
- 2000 active cases.
- Architecture must support horizontal worker scaling without schema changes.

## 4. Security

- Enforce authenticated access for all non-health endpoints.
- Enforce role-based authorization for write operations.
- Encrypt sensitive data at rest and in transit.
- Maintain immutable audit log for privileged actions.

## 5. Compliance and Privacy

- Retain operational and compliance records for minimum 7 years unless superseded by policy.
- Restrict personally identifiable information visibility by role.
- Support legal hold flag to block retention-policy deletion.

## 6. Observability

- Structured logs with correlation/request IDs.
- Metrics for API latency, queue depth, job failures, and transition failure rates.
- Metrics for AI latency, failure rates, token usage, and recommendation acceptance/rejection ratio.
- Traceability for high-latency and failed requests.
- Alert thresholds:
- API error rate > 2% for 5 minutes.
- Queue backlog > 100 pending jobs for 10 minutes.

## 7. Cost Constraints

- Paid tooling budget target: $0/month for SaaS dependencies in MVP.
- Exception: existing Google AI Pro subscription is approved.
- Infrastructure spend should stay as low as possible by favoring local/self-hosted open-source components.
