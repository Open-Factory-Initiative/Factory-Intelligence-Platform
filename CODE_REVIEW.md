# CODE_REVIEW.md

Review rubric for the Factory Intelligence Platform.

## Architecture Review

Check that the change:

- Aligns with `docs/ARCHITECTURE.md`
- Preserves service boundaries
- Uses the unified factory event model when passing operational data
- Separates source adapters from normalized platform events
- Keeps detection, evidence, and governed action logic separate
- Does not hardcode demo-only behavior into production paths

## Industrial Safety Review

Check that the change:

- Does not perform autonomous high-impact action
- Requires approval for governed actions
- Logs recommendations and approvals
- Keeps evidence attached to recommendations
- Avoids unsafe writeback patterns
- Clearly labels simulator/demo behavior

## Testing Review

Check that the change includes:

- Unit tests for logic
- Integration tests for service boundaries
- Contract tests for schemas/APIs when contracts change
- E2E tests for user workflows when UI/API behavior changes
- Negative tests for invalid input and failure modes

## Documentation Review

Check that the change updates:

- README or quickstart if setup changed
- Architecture docs if design changed
- Testing docs if commands changed
- API/data contract docs if schemas changed
- Learning log for educational context

## Security Review

Check that the change:

- Does not include secrets
- Uses environment variables for configuration
- Validates external inputs
- Does not expose unsafe debug endpoints
- Handles auth boundaries where relevant
- Keeps audit logs for governed actions

## Open-Source Review

Check that the change:

- Is understandable to new contributors
- Uses compatible dependencies
- Includes useful issue/PR context
- Avoids unnecessary complexity
- Has comments where domain knowledge is non-obvious

## Done Criteria

A PR is ready when:

- The implementation matches the request.
- Tests pass or failures are clearly documented.
- Docs are updated.
- Risky decisions are captured in an ADR.
- The change is small enough to review.
