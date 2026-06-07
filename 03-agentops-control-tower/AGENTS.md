# AGENTS.md

## Project Purpose

AgentOps Control Tower is a local observability and governance layer for AI
automation workflows.

It will eventually aggregate local workflow signals from Project 1 and Project 2:

- workflow run history
- approval states
- failure records
- retry and cadence metadata
- notification status
- LLM and token usage metadata when available
- guardrail outcomes
- local auditability evidence

## Permanent Project 3 Rules

- Work on feature branches, not directly on `main`.
- Every new function, method and class created by Codex must include a clear
  Google-style docstring.
- Every milestone must update relevant `README.md` files.
- Every milestone must update
  `docs/CODEX_HANDOFF_AI_AUTOMATION_PORTFOLIO.md`.
- Every milestone must create or update its own prompt-history file under
  `03-agentops-control-tower/docs/prompt-history/`.
- Prompt-history files must include the full prompt, expected verification,
  result summary, verification results and commit or PR placeholder.
- Documentation must stay in English.
- Do not hardcode secrets.
- Do not add real external service credentials.
- Do not overclaim features that are not implemented.
- Keep verification commands explicit.

## Current Scope

Milestone 4 adds a local reviewer-friendly CLI and deterministic Markdown
report export over the existing ingestion, summary and timeline views.

Do not implement dashboards, UI, database persistence, schedulers, external
integrations or notification providers in this milestone.

## Safety Boundaries

- Keep Project 3 local-first and deterministic.
- Do not call external APIs.
- Do not require secrets.
- Do not mutate Project 1 artifacts.
- Do not mutate Project 2 artifacts unless a future milestone explicitly allows
  a documentation link update.
- Do not implement destructive tools.
