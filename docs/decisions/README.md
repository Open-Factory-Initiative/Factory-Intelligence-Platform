# Architecture Decision Records

Architecture Decision Records (ADRs) explain important technical and product
architecture choices for the Factory Intelligence Platform. They should make the
reasoning behind a decision visible to future contributors, not just record the
final answer.

## When to Create an ADR

Create an ADR when a decision affects how the platform is shaped or safely
operated over time. Examples include:

- event model or data contract design
- storage strategy and schema boundaries
- connector or source adapter architecture
- governed action lifecycle and human approval rules
- validation, testing, or evidence requirements
- security, audit, or deployment model decisions
- major framework, language, or service-boundary choices

Do not create an ADR for small implementation details, typo fixes, local
refactors, or changes that are easy to reverse and do not affect contributor
understanding.

## ADR Process

1. Copy [ADR_TEMPLATE.md](./ADR_TEMPLATE.md) to a numbered file such as
   `0002-short-title.md`.
2. Use the next available number in `docs/decisions`.
3. Start the status as `Proposed` unless the decision has already been accepted.
4. Fill in the context, decision, options considered, consequences, follow-up
   work, and related links.
5. Submit the ADR with the pull request that introduces or depends on the
   decision.
6. If a later decision replaces it, update the old ADR status to point to the
   superseding ADR instead of deleting the history.

## Existing Decisions

- [ADR 0001: Simulator-First Modular Platform Architecture](./0001-platform-architecture.md)
