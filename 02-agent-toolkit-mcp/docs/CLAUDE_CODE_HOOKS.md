# Claude Code Hook Examples

Project 2 includes Claude Code hook-style examples under
`hooks/claude-code/`. They are local-only examples for pre-tool and post-tool
guardrails.

These scripts are not a complete security layer. They demonstrate practical
checks that can be adapted to a Claude Code configuration.

## Pre-Tool-Use Example

```bash
COMMAND='uv run pytest' 02-agent-toolkit-mcp/hooks/claude-code/pre-tool-use-check.sh
```

The script reads `TOOL_INPUT` and `COMMAND` when present. It blocks obvious
unsafe command intent such as broad destructive deletion, dangerous `sudo`
operations, credential file reads and shell execution piped from download
commands.

It intentionally does not claim complete command safety.

## Post-Tool-Use Audit

```bash
02-agent-toolkit-mcp/hooks/claude-code/post-tool-use-audit.sh
```

The audit runs safe local checks:

- `git diff --check`;
- Bash syntax checks for Project 2 scripts and hook examples;
- shared no-secrets guardrail.

It does not mutate files or commit automatically.

## Stop on Dirty Runtime

```bash
02-agent-toolkit-mcp/hooks/claude-code/stop-on-dirty-runtime.sh
```

This wrapper calls the shared Project 1 runtime-clean check through the
existing Project 2 CLI. It fails when generated Project 1 runtime artifacts are
present and never deletes them.

## Boundaries

- No external APIs.
- No secrets.
- No destructive cleanup.
- No Project 1 code or runtime behavior changes.
- No claim of deployed MCP transport.
- No claim that pending approval records are approved actions.
