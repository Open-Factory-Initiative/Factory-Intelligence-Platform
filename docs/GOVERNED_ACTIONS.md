# Governed Actions

## Purpose

The Factory Intelligence Platform should help humans make better decisions. It should not silently perform high-impact industrial actions.

A governed action is any recommendation or action that could affect production, quality, maintenance, materials, compliance, or safety.

## MVP Rule

In the MVP, all actions are recommendations. The platform may propose action, but a human must approve or reject it.

Future AI-generated outputs follow the same rule. Model summaries, RCA/CAPA
draft language, investigation suggestions, similar-event matches, and drift
explanations are advisory decision support. They must be tied to evidence,
shown for human review, and routed through governed recommendation states before
any high-impact action is considered.

## Action Categories

### Low Impact

Examples:

- Add note to detection
- Generate RCA draft
- Mark evidence as reviewed
- Update local demo state

May be allowed with simple user confirmation.

### Medium Impact

Examples:

- Recommend containment
- Recommend inspection
- Recommend engineering review
- Recommend work order hold in demo state

Requires explicit approval.

### High Impact

Examples:

- Write to MES/QMS/ERP
- Release product
- Quarantine product
- Change machine parameter
- Close deviation
- Create CAPA in production system

Out of scope for MVP except as simulated recommendations.

## Recommendation Requirements

Every recommendation must include:

- Detection ID
- Summary
- Rationale
- Evidence IDs
- Risk level
- Impact category
- Required approval state
- Created timestamp
- Audit trail

## Approval States

```text
draft
proposed
needs_review
approved
rejected
deferred
executed
closed
```

## Audit Requirements

Every decision must create an audit event with:

- Actor
- Timestamp
- Entity
- Decision
- Reason
- Before/after state when applicable

## UI Requirements

The UI must make it clear that:

- The system is recommending, not autonomously acting.
- The user is responsible for approval.
- Evidence supports the recommendation.
- The action state is tracked.
- Simulator/demo behavior is labeled.

## Future Action Dispatcher

A future production-grade action dispatcher must support:

- Role-based approvals
- Policy checks
- Dry-run mode
- External system adapters
- Transaction logs
- Reversal or cancellation when possible
- Audit exports
- Approval chains

AI agents must not bypass this dispatcher or directly call tools that change
factory state. Early agents should be limited to read-only analysis,
evidence summarization, RCA/CAPA draft support, investigation path suggestions,
similar prior event lookup, and drift signal explanation.
