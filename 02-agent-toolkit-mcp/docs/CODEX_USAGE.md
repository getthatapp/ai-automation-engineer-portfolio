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

