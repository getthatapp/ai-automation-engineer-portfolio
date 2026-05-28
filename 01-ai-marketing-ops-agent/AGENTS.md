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

## Commands

```bash
uv sync
uv run pytest
uv run ruff check .
uv run mypy src
```
