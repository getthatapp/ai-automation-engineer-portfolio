# Claude Code Permission Profiles

These profiles describe safe local ways to use Claude Code with Project 2.
They mirror the Codex profiles so both agent surfaces share the same safety
model.

## Read-Only Inspection

Purpose: inspect docs, command templates and Project 1 artifacts without file
changes.

Allowed operations:

- Read repository files.
- Preview Claude Code command templates.
- Run read-only Project 2 adapter scripts.
- Run hook-style examples in read-only mode.
- Summarize deterministic outputs.

Blocked operations:

- Editing Project 1 code.
- Deleting generated artifacts.
- Calling external APIs.
- Inferring missing run history, approvals or report contents.

Suggested Codex usage: use equivalent Codex prompts when moving the same review
to Codex.

Suggested Claude Code usage: run `inspect-project1-runtime`,
`review-project1-report` or `summarize-project1-demo-readiness` command
templates with local evidence.

Use this profile for local review workflows.

Do not use it for implementation tasks.

## Workspace-Write Development

Purpose: allow scoped Project 2 edits for docs, examples, command templates,
prompts and non-destructive scripts.

Allowed operations:

- Edit Project 2 documentation and examples.
- Update Claude Code command templates.
- Add non-destructive helper scripts.
- Run local Project 2 verification commands.

Blocked operations:

- Project 1 code changes.
- Destructive tools or cleanup commands.
- Credentials, tokens or real integration settings.
- Claims that command templates execute external MCP clients.

Suggested Codex usage: apply the same workspace-write boundary when Codex is
the implementation surface.

Suggested Claude Code usage: keep command updates explicit, auditable and
paired with verification.

Suggested hook usage: adapt `hooks/claude-code/` examples for local lifecycle
checks without adding destructive behavior or external calls.

Use this profile for safe Project 2 development.

Do not use it for external deployments or broad infrastructure work.

## Approval-Required Operations

Purpose: document actions that need explicit human approval before execution.

Allowed operations after approval:

- Dependency installation or resolution when local caches are incomplete.
- Branch, merge, commit or PR operations.
- Commands requiring broader local permissions.
- Future elevated but non-destructive MCP setup steps.

Blocked operations:

- Destructive commands without explicit user approval.
- External service calls without a milestone that implements them.
- Secret-backed configuration examples.
- Approval bypasses for sensitive operations.

Suggested Codex usage: ask for approval before escalation and keep the approved
scope narrow.

Suggested Claude Code usage: treat hooks and command wrappers as approval
boundaries when future milestones add them.

Use this profile for controlled elevation.

Do not use it as a default operating mode.

## Blocked / Destructive Operation Policy

Purpose: keep destructive behavior outside Project 2.

Allowed operations: none by default.

Blocked operations:

- Removing Project 1 runtime artifacts.
- Mutating approval queue records.
- Adding tools that delete, deploy or call real services.
- Hardcoding credentials.
- Treating pending approvals as approved actions.

Suggested Codex usage: redirect to read-only inspection or documented approval
flows.

Suggested Claude Code usage: keep command templates and examples free of
destructive shell operations.

Use this policy whenever an operation could harm auditability.

Do not add destructive capabilities to Project 2 examples.
