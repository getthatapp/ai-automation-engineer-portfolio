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
