# Contributing

Thank you for contributing to the Factory Intelligence Platform.

This project is part of the Open Factory Initiative, a community building open-source infrastructure for intelligent, connected, and AI-ready factories.

## Ways To Contribute

- Improve documentation
- Add tests
- Add simulator scenarios
- Improve UI workflows
- Add event schemas
- Build connector stubs
- Review architecture
- Write examples
- Create diagrams
- Report issues

## Before You Start

Please read:

- `README.md`
- `AGENTS.md`
- `docs/ARCHITECTURE.md`
- `docs/MVP_SCOPE.md`
- `docs/TESTING.md`
- `CODE_REVIEW.md`

## Development Workflow

1. Fork or branch from `main`.
2. Keep changes small.
3. Add tests.
4. Update docs.
5. Open a pull request.
6. Explain what changed and how it was tested.

## Local Validation

The baseline CI workflow uses the same Makefile commands contributors should run
locally before opening a pull request:

```bash
make setup
make lint
make typecheck
make test
```

Run narrower suites while iterating:

```bash
make test-unit
make test-integration
make test-contract
```

`make test-e2e` is currently a documented placeholder until the web workbench is
implemented.

## Pull Request Checklist

- [ ] I linked the relevant issue and used `Closes #issue-number` when the PR should close it.
- [ ] I summarized what changed and why.
- [ ] I read the relevant docs.
- [ ] I kept the change focused.
- [ ] I added or updated tests.
- [ ] I updated documentation.
- [ ] I included test evidence and reviewer notes in the pull request template.
- [ ] I did not add secrets.
- [ ] I did not add unsafe industrial writeback behavior.
- [ ] I updated `docs/LEARNING_LOG.md` if this is a meaningful feature/change.

## Code Style

Prefer clarity over cleverness.

Use:

- Type hints for Python
- TypeScript types for frontend code
- Explicit schemas for contracts
- Structured logs
- Small modules
- Tests close to behavior

## Industrial Safety

Do not add direct writeback to real industrial systems without a design discussion, governance model, audit requirements, and maintainer approval.
