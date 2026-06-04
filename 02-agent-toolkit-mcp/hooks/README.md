# Hooks and Guardrails

This directory contains local-only examples for agent guardrails.

- `shared/` contains reusable read-only checks.
- `codex/` contains Codex guardrail wrappers and hook-equivalent workflows.
- `claude-code/` contains Claude Code hook-style examples.

These scripts are deterministic examples. They do not call external APIs,
require secrets, delete files, mutate Project 1 or commit automatically.

They are not a complete security system. Use them as portfolio-ready examples
of practical safety boundaries around local agent workflows.
