# Codex Hook-Equivalent Guardrails

Codex does not use the same hook lifecycle model as Claude Code. Project 2
therefore provides hook-equivalent guardrail wrappers for Codex workflows.

Use these scripts as local preflight and post-run checks around a Codex
milestone execution. They do not invoke Codex and do not mutate files.

## Preflight

Run before implementation:

```bash
PROMPT_HISTORY_FILE=02-agent-toolkit-mcp/docs/prompt-history/milestone-08-dual-agent-guardrails.md \
  02-agent-toolkit-mcp/hooks/codex/preflight-codex-run.sh
```

The preflight wrapper:

- blocks work on `main` unless `ALLOW_MAIN=true`;
- warns on dirty worktrees by default;
- fails on dirty worktrees when `STRICT_WORKTREE=true`;
- validates prompt-history structure when `PROMPT_HISTORY_FILE` is set;
- prints a recommended sandboxed and approval-aware Codex mode.

## Prompt History

To require a prompt-history file explicitly:

```bash
PROMPT_HISTORY_FILE=02-agent-toolkit-mcp/docs/prompt-history/milestone-08-dual-agent-guardrails.md \
  02-agent-toolkit-mcp/hooks/codex/require-prompt-history.sh
```

This is a structural check for required sections. It does not write missing
content and does not verify that the implementation is complete.

## Post-Run Audit

Run after implementation:

```bash
02-agent-toolkit-mcp/hooks/codex/postrun-codex-audit.sh
```

The post-run wrapper runs Project 2 checks, shell syntax validation, whitespace
diff checks and the shared no-secrets guardrail. It never commits
automatically.

## Recommended Codex Pattern

1. Read `AGENTS.md`, handoff docs and the current milestone prompt.
2. Run a preflight wrapper.
3. Implement within the documented permission profile.
4. Run deterministic checks.
5. Update prompt history with actual results.
6. Run the post-run audit.

This is a local operating pattern, not a claim that Codex has Claude Code hook
parity.
