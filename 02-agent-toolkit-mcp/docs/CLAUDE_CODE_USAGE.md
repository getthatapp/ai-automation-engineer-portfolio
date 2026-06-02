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
