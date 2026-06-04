# Shared Guardrails

Shared guardrails are reusable by both Codex wrapper flows and Claude Code
hook-style examples.

Scripts:

- `check-no-secrets.sh`: conservative scan for obvious secret-like assignments
  or token-looking values in selected repository files.
- `check-runtime-clean.sh`: read-only Project 1 runtime artifact check through
  the existing `agent-toolkit-mcp` CLI.
- `check-prompt-history-updated.sh`: verifies that a milestone prompt-history
  file exists and contains required sections.

These checks print pass/fail output and return non-zero when a guardrail fails.
They do not modify files.
