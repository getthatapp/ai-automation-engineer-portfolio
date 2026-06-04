# Claude Code Usage

Claude Code-oriented workflows in this project are guided by `CLAUDE.md`,
command templates under `claude-commands/` and shared skills under `skills/`.

## Command Pattern

Each Claude Code command should include:

- purpose;
- expected inputs;
- safety constraints;
- execution steps;
- review checklist;
- verification commands.

## Running a Command Template

Preview a command from the project directory:

```bash
./scripts/run_claude_command.sh review-workflow
./scripts/run_claude_command.sh inspect-project1-runtime
./scripts/run_claude_command.sh review-project1-report
./scripts/run_claude_command.sh summarize-project1-demo-readiness
```

The helper prints the template path and content. It does not invoke Claude Code
or call external services.

## Claude Code Positioning

Claude Code commands should be useful for repeatable engineering tasks such as
reviewing workflows, generating runbooks and investigating CI failures. Future
milestones may add hooks and executable command integration.

Select the narrowest documented permission profile for the task. Current
profiles are guidance for local use, not enforced runtime policy.

## MCP Tool Usage

The local MCP tool package under `mcp-server/` is designed to become a
read-only Project 1 inspection tool source for Claude Code. Current tools can
validate reports, inspect run history, summarize pending approvals, report
runtime artifacts and generate deterministic demo readiness briefs.

This milestone does not add external MCP client configuration or hooks. Future
Claude Code integration should keep these tools local-only, deterministic and
credential-free.

Run package checks with:

```bash
./scripts/run_mcp_checks.sh
```

Run the full Project 2 CI mirror locally:

```bash
./scripts/run_ci_locally.sh
```

The CI mirror runs local deterministic scaffold, MCP server and CLI smoke
checks. It does not call external APIs, require secrets, run Docker services,
deploy anything or mutate Project 1 artifacts.

Milestone 6 adds direct local CLI invocation for deterministic tool evidence:

```bash
cd 02-agent-toolkit-mcp/mcp-server
uv run agent-toolkit-mcp validate-report ../../01-ai-marketing-ops-agent/reports/example.md
uv run agent-toolkit-mcp read-run-history ../../01-ai-marketing-ops-agent/run-history/workflow-runs.jsonl --limit 5
uv run agent-toolkit-mcp list-pending-approvals ../../01-ai-marketing-ops-agent/approval-requests/approval-requests.jsonl
uv run agent-toolkit-mcp check-runtime-clean ../../01-ai-marketing-ops-agent
uv run agent-toolkit-mcp generate-demo-brief ../../01-ai-marketing-ops-agent --pretty
```

The CLI is local-only and prints JSON. It is a shell interface to existing
deterministic functions, not a deployed MCP transport or external integration.

## Project 1 Agent Review Flows

Milestone 3 adds Claude Code command templates that mirror the Codex Project 1
review prompts:

- `inspect-project1-runtime`: inspect local runtime artifacts, run history and
  pending approval summaries.
- `review-project1-report`: validate a local report and summarize deterministic
  evidence.
- `summarize-project1-demo-readiness`: summarize local demo readiness without
  claiming production deployment or external integration.

Use the local adapter scripts to gather evidence:

```bash
./scripts/demo_mcp_tools.sh
./scripts/run_project1_tool_review.sh
```

These commands are local-only and read-only. They do not invoke Claude Code,
call external APIs, require secrets or mutate Project 1 runtime artifacts.

## Permission Profiles

Milestone 4 documents Claude Code runtime profiles in
`docs/runtime/CLAUDE_CODE_PERMISSION_PROFILES.md`:

- read-only inspection;
- workspace-write development;
- approval-required operations;
- blocked/destructive operation policy.

Preview the local profiles:

```bash
./scripts/show_permission_profiles.sh
```

Use read-only inspection for local artifact review. Use workspace-write for
scoped Project 2 command, docs and non-destructive script updates. Use
approval-required operations for dependency resolution, branch work or future
elevated local setup. Destructive operations remain unsupported.
