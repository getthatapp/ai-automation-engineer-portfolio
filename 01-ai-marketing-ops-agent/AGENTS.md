# AGENTS.md

## Project Purpose

`01-ai-marketing-ops-agent` is the first portfolio project: a production-oriented
AI Marketing Operations Agent.

The target workflow will collect campaign data from a mock marketing panel,
REST APIs and GraphQL APIs, validate it, detect anomalies, request human approval
for sensitive actions, use an LLM only for interpretation, and produce an
auditable Markdown report.

## Current Milestone

This milestone is scaffold-only. Do not implement the full Playwright workflow
yet.

Included now:

- Python 3.12+ project using `uv`.
- Pydantic v2 domain models.
- Retry and rate limiter utilities.
- Minimal pytest coverage.
- Documentation placeholders.
- Local marketing report skill.

## Engineering Rules

- Keep deterministic logic outside LLM prompts.
- Use APIs when an API exists.
- Use Playwright only for panels without an API.
- Add timeouts and error handling for every external call.
- Log every workflow run.
- Do not bypass real CAPTCHA.
- Use human approval checkpoints before sensitive actions.
- Do not hardcode secrets.
- Keep generated logs, reports, caches and `.env` out of git.

## Docstring rules

Every function, method and class created or modified by Codex must include a
clear Google-style docstring. A useful docstring should explain what the
function or class does, important arguments, return value, raised exceptions
when relevant, and meaningful side effects such as file writes, JSONL
persistence, API calls, browser automation, report generation, workflow
orchestration, LLM provider calls or mock provider behavior. Docstrings should
be concise and useful; they must not merely repeat the function or class name.
For simple Pydantic models and enums, add class docstrings where they improve
clarity, but do not over-document obvious fields. For private helpers, add
docstrings when the function contains non-trivial behavior, validation logic,
branching rules, external calls or side effects.

## Commands

```bash
uv sync
uv run pytest
uv run ruff check .
uv run mypy src
```
