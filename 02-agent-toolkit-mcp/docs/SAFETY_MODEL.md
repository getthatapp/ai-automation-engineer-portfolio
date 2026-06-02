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

## Tool Behavior

MCP tools should:

- validate inputs;
- use deterministic operations;
- return structured, auditable outputs;
- fail safely with clear error messages;
- avoid vague LLM reasoning inside tool implementations.

## External Integrations

This scaffold does not call external services. Future integrations should be
mocked by default in tests and local demos, with real credentials supplied only
through environment variables.

## Auditability

Workflows should preserve enough context for a reviewer to understand:

- what input was used;
- what operation ran;
- what changed;
- what verification passed;
- what requires human approval.

