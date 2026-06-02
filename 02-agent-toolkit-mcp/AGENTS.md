# AGENTS.md

## Project Purpose

Project 2 is the Agent Toolkit for Codex and Claude Code.

It is a reusable toolkit for building, running and reviewing agentic automation
workflows. It should support Codex-oriented workflows, Claude Code-oriented
workflows, shared skills and future deterministic MCP tools.

## Branch Workflow

- Assume work is done on a feature branch.
- Do not assume direct work on `main`.
- Keep changes scoped to Project 2 and portfolio documentation unless the user
  explicitly requests otherwise.
- Do not modify Project 1 code unless explicitly requested.

## Permanent Project 2 Rules

- Every new function, method and class created by Codex must include a clear
  Google-style docstring.
- Every milestone must update the relevant README files.
- Every milestone must update `docs/CODEX_HANDOFF_AI_AUTOMATION_PORTFOLIO.md`.
- Documentation must stay in English.
- Do not hardcode secrets.
- Do not add real external service credentials.
- Do not overclaim features that are not implemented.
- Keep verification commands explicit.

## Architecture Rules

- MCP tools should perform deterministic operations with typed inputs, input
  validation, timeouts where relevant and auditable outputs.
- MCP tools should not contain vague LLM reasoning or hidden approval decisions.
- Codex workflows should use `AGENTS.md`-oriented guidance and explicit prompt
  templates.
- Claude Code workflows should use `CLAUDE.md`-oriented guidance plus command,
  hook and skill conventions.
- Shared skills should be agent-neutral where practical.

## Safety Rules

- No hardcoded secrets, tokens, API keys or real credentials.
- No destructive actions without explicit user approval.
- No real external integrations in the scaffold milestone.
- Future tools must validate inputs before execution.
- Future workflows must preserve auditability through clear inputs, outputs,
  logs and run records.

## Verification Rules

For this scaffold milestone, run:

```bash
bash -n 02-agent-toolkit-mcp/scripts/*.sh
02-agent-toolkit-mcp/scripts/run_checks.sh
git diff --check
```

Future milestones should add project-specific tests and checks as implementation
scope grows.

