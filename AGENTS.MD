# AGENTS.md

## Repository purpose

This repository is an AI Automation Engineer portfolio.

It contains three production-oriented demo projects:
- 01-ai-marketing-ops-agent
- 02-mcp-automation-server-claude-toolkit
- 03-agentops-control-tower

The goal is not to build chatbots. The goal is to demonstrate practical AI automation:
LLM agents, Playwright browser automation, REST/GraphQL integrations, MCP tools,
skills, hooks, observability, retries, fallbacks, human approval and documentation.

## Primary instructions

Before implementing anything, read:

- docs/CODEX_HANDOFF_AI_AUTOMATION_PORTFOLIO.md

Start with:

- 01-ai-marketing-ops-agent

## Coding standards

- Prefer small, focused commits.
- Do not hardcode secrets.
- Use `.env.example` for configuration examples.
- Keep generated reports, logs, caches and local env files out of git.
- Add tests for every meaningful module.
- Keep code simple, typed and production-oriented.
- Document architectural decisions in `docs/`.

## Project 1 rules

For `01-ai-marketing-ops-agent`:

- Python 3.12+
- uv for dependency management
- Pydantic v2
- FastAPI for mock services
- Playwright for browser automation
- pytest for tests
- ruff for linting
- mypy-ready code structure
- Docker Compose for local services

## Architecture rules

- Use API integration when an API exists.
- Use Playwright only for panels without API.
- Use LLM only for interpretation, summarization and recommendations.
- Deterministic code must handle scraping, validation, retries, persistence and logging.
- Every workflow run must be logged.
- Every external call must have timeout and error handling.
- Do not bypass real CAPTCHA.
- Use human approval checkpoints for sensitive actions.

## Current milestone

Create the initial scaffold for `01-ai-marketing-ops-agent`.

Do not implement the full Playwright workflow yet.
First milestone should include:
- project structure
- pyproject.toml
- README.md
- AGENTS.md inside project folder
- .env.example
- docs placeholders
- skill folder
- basic Pydantic models
- retry utility
- rate limiter utility
- minimal tests