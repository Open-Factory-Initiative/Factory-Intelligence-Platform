# Documentation Standards

## Purpose

Documentation is part of the product. It should help new contributors understand manufacturing context, platform architecture, and how to extend the system safely.

## Documentation Types

### README

The root README should explain:

- What the project is
- Why it exists
- How to run it
- How to test it
- Where to contribute

### Architecture Docs

Architecture docs should explain:

- Service boundaries
- Data flow
- Event contracts
- Governance model
- Deployment assumptions

### ADRs

Architecture Decision Records should capture important decisions.

Use `docs/decisions/`.

### API Docs

API docs should be generated or synchronized from backend models when possible.

### Learning Docs

Learning docs explain how the platform works for the maintainer and contributors.

Use:

```text
docs/LEARNING_MODE.md
docs/LEARNING_LOG.md
```

## Mermaid Diagrams

Use Mermaid for diagrams when possible because it renders in GitHub Markdown.

Recommended diagram types:

- `flowchart`
- `sequenceDiagram`
- `erDiagram`

## Writing Style

- Be direct.
- Avoid unexplained manufacturing jargon.
- Define acronyms on first use.
- Include examples.
- Keep docs close to the feature they explain.
- Update docs in the same PR as behavior changes.

## Required Docs For New Features

A new feature should include:

- Usage instructions
- Test instructions
- Relevant architecture notes
- Example payloads if APIs/events changed
- Learning log entry

## Documentation Review Checklist

- Is the doc accurate?
- Can a new contributor follow it?
- Does it explain why, not only what?
- Are commands current?
- Are diagrams consistent with implementation?
- Are assumptions explicit?
