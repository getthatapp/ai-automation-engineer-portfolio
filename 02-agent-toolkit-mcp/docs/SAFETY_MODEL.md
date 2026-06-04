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
- Milestone 4 permission profiles document read-only, workspace-write,
  approval-required and blocked/destructive operating modes for local agent
  workflows.

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

Milestone 6 adds a CLI wrapper around these same tools. The wrapper prints JSON
evidence and returns status-check exit codes, but does not add new tool
capabilities, external calls or write operations.

Milestone 8 adds hook and guardrail examples around the same local boundaries.
They are read-only examples and do not provide complete security enforcement.

JSONL-reading tools sanitize secret-like keys and obvious bearer/API-token
values before returning records to an agent.

Milestone 5 strengthens the current tools with explicit symlink resolution,
structured non-fatal report warnings, record counts, artifact counts and
readiness checklists. These additions improve auditability without adding write
operations or external calls.

## External Integrations

This scaffold does not call external services. Future integrations should be
mocked by default in tests and local demos, with real credentials supplied only
through environment variables.

Milestone 3 adapter scripts and prompt/command templates are local-only. They
do not invoke Codex, Claude Code, external MCP clients or third-party APIs.

Milestone 4 runtime examples are documentation only. They do not add external
MCP deployment, external service calls, credentials or destructive operations.

Milestone 6 CLI usage remains local-only and should not be described as a real
deployed MCP service.

Milestone 8 guardrails should not be described as exact Codex/Claude Code hook
parity or as comprehensive secret/security scanning.

## Auditability

Workflows should preserve enough context for a reviewer to understand:

- what input was used;
- what operation ran;
- what changed;
- what verification passed;
- what requires human approval.

## Runtime Profile Documentation

See `docs/runtime/` for:

- local MCP/runtime configuration;
- Codex permission profiles;
- Claude Code permission profiles;
- local-only security boundaries;
- troubleshooting guidance.
