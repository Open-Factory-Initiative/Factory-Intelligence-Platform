# Learning Mode

## Purpose

The maintainer wants Codex to teach how the Factory Intelligence Platform works while building it.

Codex should produce code, tests, and documentation, but it should also explain the platform in practical terms.

## Learning Log

Maintain:

```text
docs/LEARNING_LOG.md
```

Every meaningful task should add an entry.

## Entry Format

```markdown
## YYYY-MM-DD - <task name>

### What changed

### Why it matters

### How it works

### How to run it

### How to test it

### Key files

### What to learn next
```

## Teaching Style

Codex should explain:

- The manufacturing concept
- The software architecture concept
- The data flow
- The testing strategy
- The safety/governance implication

## Example

```markdown
## 2026-05-08 - Added simulator event schema

### What changed

Added a normalized process measurement event schema.

### Why it matters

The rest of the platform needs a stable event format so ingestion, storage, detection, and UI services can communicate.

### How it works

The simulator emits a raw process value. The ingestion service wraps it in the platform event envelope and validates the required context fields.

### How to test it

Run contract tests for valid and invalid process measurement fixtures.

### What to learn next

Learn how event schemas support a Unified Namespace.
```
