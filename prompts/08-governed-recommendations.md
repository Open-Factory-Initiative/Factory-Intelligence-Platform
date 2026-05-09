# Prompt 08: Governed Recommendations

Act as a senior safety-conscious industrial software engineer.

Goal: implement the governed recommendation workflow.

Requirements:

- Create recommendation from detection + evidence
- Support states: draft, proposed, needs_review, approved, rejected, deferred, closed
- Require human approval for action
- Record approval decisions
- Write audit events
- Include tests for state transitions
- Include negative tests for invalid transitions
- Update `docs/GOVERNED_ACTIONS.md`
- Update learning log

Do not implement real writeback to external industrial systems.
