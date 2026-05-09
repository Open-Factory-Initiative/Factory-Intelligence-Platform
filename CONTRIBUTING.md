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

## Pull Request Checklist

- [ ] I read the relevant docs.
- [ ] I kept the change focused.
- [ ] I added or updated tests.
- [ ] I updated documentation.
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
