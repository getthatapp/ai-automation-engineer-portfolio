# Codex Guardrail Wrappers

Codex does not have the same hook lifecycle model as Claude Code. These scripts
are hook-equivalent guardrail wrappers for local Codex workflows:

- `preflight-codex-run.sh`: run before a Codex milestone execution.
- `postrun-codex-audit.sh`: run after implementation to collect local evidence.
- `require-prompt-history.sh`: enforce prompt-history structure.

They are local-only examples. They do not invoke Codex, call external APIs,
mutate files, commit automatically or replace human review.
