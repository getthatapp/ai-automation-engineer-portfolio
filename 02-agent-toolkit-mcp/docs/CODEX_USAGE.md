# Codex Usage

Codex-oriented workflows in this project are guided by `AGENTS.md` and reusable
prompt templates under `codex-prompts/`.

## Prompt Pattern

Each Codex prompt should include:

- current state;
- goal;
- implementation scope;
- safety constraints;
- files or modules to inspect;
- verification commands;
- expected summary format.

## Running a Prompt Template

Preview a prompt from the project directory:

```bash
./scripts/run_codex_prompt.sh review-workflow
```

The helper prints the template path and content. It does not invoke Codex or
call external services.

## Safety Expectations

- Use deterministic code for validation, parsing and tool execution.
- Keep LLM reasoning separate from deterministic operations.
- Do not hardcode secrets.
- Do not run destructive commands without explicit approval.
- Keep all changes scoped to the requested project area.

## MCP Tool Usage

The local MCP tool layer under `mcp-server/` can conceptually support Codex
reviews of Project 1 artifacts. Codex can use the deterministic tools to:

- validate that a generated Markdown report contains the expected sections;
- inspect recent workflow run history without exposing secret-like values;
- list pending approval request summaries;
- report whether generated runtime artifacts are present;
- generate a local-only Project 1 demo readiness brief.

Current transport wiring is intentionally minimal. Run package checks with:

```bash
./scripts/run_mcp_checks.sh
```
