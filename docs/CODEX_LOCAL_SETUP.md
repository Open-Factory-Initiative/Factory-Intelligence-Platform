# Codex Local Setup

## Install

```bash
npm i -g @openai/codex
```

## Run

From the repository root:

```bash
codex
```

The first run will prompt for authentication.

## Useful Slash Commands

- `/plan` — ask Codex to plan before coding
- `/review` — ask Codex to review your working tree
- `/status` — inspect session/model/config status
- `/model` — change model or reasoning level when available
- `/mention` — attach a specific file or folder for context
- `/new` — start a fresh context in the same CLI session

## Recommended Startup Prompt

```text
Read AGENTS.md, PLANS.md, CODE_REVIEW.md, docs/START_HERE_FOR_CODEX.md, docs/ARCHITECTURE.md, docs/MVP_SCOPE.md, and docs/TESTING.md. Do not write code yet. Inspect the repo and propose the next smallest implementation plan.
```

## Suggested Personal Global AGENTS.md

Optional file:

```text
~/.codex/AGENTS.md
```

Suggested content:

```markdown
# Personal Codex Preferences

- Be concise but explain important tradeoffs.
- Prefer small, reviewable changes.
- Ask for a plan before broad changes.
- Always list test commands run.
- Do not add dependencies without explaining why.
```
