# Project Foundation Status

This document maps the project foundation epic to the repository files that
currently satisfy it.

Issue: https://github.com/Open-Factory-Initiative/Factory-Intelligence-Platform/issues/7

Last verified: 2026-05-15

## Foundation Surfaces

The repository foundation is intentionally small and open-source friendly:

- Contributor onboarding: `CONTRIBUTING.md`
- Local setup and MVP run loop: `README.md` and `docs/DEVELOPMENT.md`
- Repository structure: `README.md`, `CONTRIBUTING.md`, and `FILE_INDEX.md`
- Coding and review standards: `CODE_REVIEW.md`, `AGENTS.md`, and
  `docs/TESTING.md`
- Issue templates: `.github/ISSUE_TEMPLATE/`
- Pull request template: `.github/pull_request_template.md`
- Baseline CI: `.github/workflows/ci.yml`
- Architecture decision process: `docs/decisions/README.md` and
  `docs/decisions/ADR_TEMPLATE.md`

## Contributor Entry Points

A new contributor should start with:

1. Read `README.md` for the project goal, repository structure, and local setup.
2. Read `CONTRIBUTING.md` for issue workflow, branch naming, PR expectations,
   and test commands.
3. Run the local validation commands:

```bash
make setup
make lint
make typecheck
make test
```

4. Look for beginner-friendly work:

```text
https://github.com/Open-Factory-Initiative/Factory-Intelligence-Platform/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22
```

If no `good first issue` work is available, start with small `Task` or
documentation issues in the current milestone.

## Epic Acceptance Criteria

| Acceptance criterion | Current status |
| --- | --- |
| A new contributor can understand how to run the project locally | Covered by `README.md`, `CONTRIBUTING.md`, and `docs/DEVELOPMENT.md`. |
| A new contributor can find good first issues | Covered by `CONTRIBUTING.md` and the `good first issue` label query above. |
| CI runs on pull requests | Covered by `.github/workflows/ci.yml` with `on: pull_request`. |
| PRs have a consistent template | Covered by `.github/pull_request_template.md`. |
| Documentation explains the project structure | Covered by `README.md`, `CONTRIBUTING.md`, and `FILE_INDEX.md`. |

## Definition Of Done Evidence

| Epic item | Evidence |
| --- | --- |
| Foundation docs merged | `README.md`, `CONTRIBUTING.md`, `CODE_REVIEW.md`, `docs/DEVELOPMENT.md`, and this status document. |
| CI checks active | `.github/workflows/ci.yml` runs hygiene, backend lint, typecheck, tests, and frontend checks when a frontend package exists. |
| Templates available in the repo | `.github/ISSUE_TEMPLATE/` and `.github/pull_request_template.md`. |
| Follow-up work is tracked as issues | Foundation child issues and ongoing MVP milestone issues are tracked in GitHub Issues. |

## Foundation Child Issues

The original foundation child issues are tracked separately:

- #18 - GitHub issue templates
- #19 - Pull request template
- #20 - ADR template
- #21 - Contributor onboarding guide
- #22 - Baseline CI workflow
- #23 - Local developer setup verification

The remaining work for future MVP hardening should continue as focused issues
rather than expanding the foundation epic.
