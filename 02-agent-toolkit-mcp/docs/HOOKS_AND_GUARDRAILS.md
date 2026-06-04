# Hooks and Guardrails

Project 2 provides local hook and guardrail examples for agent workflows. The
goal is to demonstrate practical safety boundaries around deterministic tools,
prompt history and verification commands.

These examples are local-only and read-only. They do not call external APIs,
require secrets, delete files, mutate Project 1, commit automatically, deploy
anything or publish packages.

## Shared Model

The shared lifecycle is:

1. Preflight: check branch, worktree and prompt-history expectations.
2. Permission profile: choose read-only, workspace-write or approval-required
   behavior before work starts.
3. Command or tool execution: run the agent or local tool within the selected
   boundary.
4. Post-run validation: run deterministic checks and collect evidence.
5. Audit output: summarize what passed, what failed and what still needs human
   review.

Claude Code can use hook-style lifecycle examples. Codex should use
hook-equivalent wrappers and documented preflight/post-run guardrails. This is
not exact hook parity.

## Local Scripts

Shared scripts:

```bash
02-agent-toolkit-mcp/hooks/shared/check-no-secrets.sh
02-agent-toolkit-mcp/hooks/shared/check-runtime-clean.sh
02-agent-toolkit-mcp/hooks/shared/check-prompt-history-updated.sh
```

Codex guardrail wrappers:

```bash
02-agent-toolkit-mcp/hooks/codex/preflight-codex-run.sh
02-agent-toolkit-mcp/hooks/codex/postrun-codex-audit.sh
02-agent-toolkit-mcp/hooks/codex/require-prompt-history.sh
```

Claude Code hook-style examples:

```bash
02-agent-toolkit-mcp/hooks/claude-code/pre-tool-use-check.sh
02-agent-toolkit-mcp/hooks/claude-code/post-tool-use-audit.sh
02-agent-toolkit-mcp/hooks/claude-code/stop-on-dirty-runtime.sh
```

Run the guardrail suite:

```bash
02-agent-toolkit-mcp/scripts/run_guardrail_checks.sh
```

## Prompt History

Milestone workflows should set `PROMPT_HISTORY_FILE` when checking a specific
prompt-history file:

```bash
PROMPT_HISTORY_FILE=02-agent-toolkit-mcp/docs/prompt-history/milestone-08-dual-agent-guardrails.md \
  02-agent-toolkit-mcp/hooks/shared/check-prompt-history-updated.sh
```

The prompt-history guardrail checks for required sections only. It does not
judge implementation quality.

## Limitations

- The no-secrets check is conservative and scoped; it is not a complete secret
  scanner.
- The Claude Code pre-tool-use example blocks obvious unsafe intent only.
- The Codex scripts are wrappers and operating patterns, not Codex lifecycle
  hooks.
- These examples do not replace sandboxing, permission profiles, code review or
  human approval.
