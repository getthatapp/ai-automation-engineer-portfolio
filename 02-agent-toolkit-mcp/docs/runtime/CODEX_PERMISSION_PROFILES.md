# Codex Permission Profiles

These profiles describe safe local ways to use Codex with Project 2. They are
documentation and operating guidance, not an enforced runtime policy.

## Read-Only Inspection

Purpose: inspect Project 1 artifacts and Project 2 docs without changing files.

Allowed operations:

- Read repository files.
- Run `run_checks.sh`, `demo_mcp_tools.sh` and `run_project1_tool_review.sh`.
- Run local guardrail wrappers in read-only mode.
- Preview Codex prompt templates.
- Summarize deterministic tool outputs.

Blocked operations:

- Editing Project 1 code.
- Deleting runtime artifacts.
- Creating credentials or external integrations.
- Claiming missing data as observed.

Suggested Codex usage: report findings from deterministic outputs and identify
missing evidence explicitly.

Suggested Claude Code usage: use the matching read-only command templates if
switching agent surfaces.

Use this profile for reviews, portfolio demos and artifact inspection.

Do not use it for implementation work that needs file edits.

## Workspace-Write Development

Purpose: update Project 2 docs, prompts, commands, scripts or tests within the
workspace.

Allowed operations:

- Edit Project 2 files.
- Add docs, examples, prompt templates and non-destructive scripts.
- Run Project 2 verification commands.
- Update Project 2 prompt history and root handoff docs.

Blocked operations:

- Project 1 code or runtime behavior changes.
- Destructive cleanup scripts.
- Real credentials or external API calls.
- Unverified claims of deployed MCP transport.

Suggested Codex usage: implement scoped Project 2 milestones and run explicit
verification before summarizing.

Suggested guardrail usage: run `hooks/codex/preflight-codex-run.sh` before
implementation and `hooks/codex/postrun-codex-audit.sh` after implementation
when the task scope calls for extra local checks.

Suggested Claude Code usage: use command templates for repeatable local tasks,
but keep writes scoped to Project 2 unless explicitly instructed otherwise.

Use this profile for documentation-first milestones and safe Project 2
implementation work.

Do not use it for production deployment, real service integration or broad repo
refactors.

## Approval-Required Operations

Purpose: gate higher-risk actions behind explicit human approval.

Allowed operations after approval:

- Branch operations such as merge or commit creation.
- Dependency resolution when local caches are missing.
- Running commands that require broader system or network access.
- Any future non-destructive operation that needs elevated permissions.

Blocked operations:

- Silent destructive changes.
- Secret creation or credential insertion.
- External side effects not covered by approval.
- Bypassing human review for sensitive actions.

Suggested Codex usage: request approval before escalation and record the reason
in the final summary or prompt history when relevant.

Suggested Claude Code usage: make permission boundaries explicit in the command
notes before running elevated actions.

Use this profile when a safe task requires approval due to sandbox, network or
branch-write constraints.

Do not use it to normalize unnecessary broad permissions.

## Blocked / Destructive Operation Policy

Purpose: define operations that Project 2 does not support.

Allowed operations: none by default.

Blocked operations:

- Deleting Project 1 reports, run history or approval queue files.
- Mutating Project 1 runtime behavior.
- Writing real credentials.
- Calling real external services.
- Adding destructive MCP tools.
- Claiming approved actions from pending approval records.

Suggested Codex usage: refuse or redirect destructive requests unless the user
explicitly authorizes a safe, scoped alternative.

Suggested Claude Code usage: keep destructive shell operations out of reusable
commands and examples.

Use this policy for all Project 2 milestones.

Do not use destructive operations as shortcuts for cleanup or verification.
