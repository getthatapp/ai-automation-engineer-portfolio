# Safety Model

Project 2 is intended to help agents run useful automation without hiding risk.

## Secrets

- Do not hardcode secrets, tokens, API keys or credentials.
- Do not add real external service credentials to examples.
- Use environment variables and `.env.example` files only when implementation
  milestones need configuration examples.

## Permissions

- No destructive action should run without explicit approval.
- Future shell wrappers should make side effects clear before execution.
- Future MCP tools should expose permission boundaries in documentation.
- Current Project 1 adapter scripts are read-only and must report runtime files
  without deleting or modifying them.

## Tool Behavior

MCP tools should:

- validate inputs;
- use deterministic operations;
- return structured, auditable outputs;
- fail safely with clear error messages;
- avoid vague LLM reasoning inside tool implementations.

The current MCP server package is local and read-only. Its tools inspect only
explicitly provided report, JSONL or project paths. Project-level tools inspect
child paths under the provided project directory and return relative paths for
auditability. They do not delete generated files, mutate approval records, call
external APIs or require credentials.

JSONL-reading tools sanitize secret-like keys and obvious bearer/API-token
values before returning records to an agent.

## External Integrations

This scaffold does not call external services. Future integrations should be
mocked by default in tests and local demos, with real credentials supplied only
through environment variables.

Milestone 3 adapter scripts and prompt/command templates are local-only. They
do not invoke Codex, Claude Code, external MCP clients or third-party APIs.

## Auditability

Workflows should preserve enough context for a reviewer to understand:

- what input was used;
- what operation ran;
- what changed;
- what verification passed;
- what requires human approval.
