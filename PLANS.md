# PLANS.md

Codex should use this file as the execution-plan template for non-trivial work.

## When To Use A Plan

Use a plan before coding when the task:

- Touches more than one service or app
- Changes architecture
- Adds a new dependency
- Adds or changes data contracts
- Adds a new workflow
- Affects testing or CI
- Changes security, governance, or industrial action behavior
- Is ambiguous

## Plan Format

```markdown
# Plan: <short task name>

## Goal

What user-visible or developer-visible outcome will this produce?

## Context Read

List the files/docs inspected before planning.

## Current State

What exists now?

## Proposed Change

What will change?

## Files To Create Or Edit

- `path/to/file`: why this file is needed

## Implementation Steps

1. Step one
2. Step two
3. Step three

## Tests

List unit, integration, contract, and e2e tests that will be added or updated.

## Documentation Updates

List docs that will be added or updated.

## Learning Update

Explain what will be added to `docs/LEARNING_LOG.md`.

## Risks / Assumptions

List anything uncertain.

## Rollback Plan

How can this change be reverted safely?
```

## Rules

- Keep plans concrete.
- Do not include vague tasks like "improve code."
- Do not start implementation until the plan is reasonable.
- For very large work, split into smaller plans.
- Prefer vertical slices over broad skeletons.
