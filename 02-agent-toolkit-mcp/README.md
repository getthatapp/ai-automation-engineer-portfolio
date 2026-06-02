# Agent Toolkit for Codex and Claude Code

Project 2 is a reusable toolkit scaffold for building, running and reviewing
agentic automation workflows with both Codex and Claude Code.

This project is not a business workflow app. Project 1 demonstrates a working
marketing operations workflow; Project 2 is the reusable agent-tooling layer
that will support future workflow development.

## Current Status

Milestone 1 is scaffold-focused.

Implemented in this milestone:

- Project documentation for a dual-agent toolkit.
- Codex prompt templates.
- Claude Code command templates.
- Shared skill documentation.
- Lightweight local scripts for scaffold checks and template discovery.
- Safety model for future MCP tools and agent workflows.

Not implemented yet:

- MCP server runtime.
- MCP tool registration.
- External service integrations.
- Real credentials or secret-backed providers.
- Deployment or CI for Project 2.

## Toolkit Concepts

### Codex Prompts

Codex prompts are reusable Markdown prompt templates intended for Codex-style
coding agents. They assume `AGENTS.md`-oriented repository guidance and explicit
task prompts that define goal, scope, constraints and verification.

### Claude Code Commands

Claude Code commands are reusable Markdown command templates intended for
Claude Code workflows. They assume `CLAUDE.md`-oriented project guidance and can
later be paired with Claude Code commands, hooks and skills.

### Shared Skills

Shared skills are reusable instructions for recurring agent tasks such as
workflow review, MCP tool design and runbook writing. They should be useful to
both Codex-style and Claude Code-style agents.

### MCP Tools

MCP tools should contain deterministic operations, typed inputs, validation,
safe error handling and auditable outputs. They should not contain vague LLM
reasoning or hidden business decisions.

## Project Structure

```text
02-agent-toolkit-mcp/
├── AGENTS.md
├── CLAUDE.md
├── README.md
├── claude-commands/
├── codex-prompts/
├── docs/
├── examples/
├── scripts/
└── skills/
```

## Local Checks

Run lightweight scaffold checks from the project directory:

```bash
./scripts/run_checks.sh
```

From the repository root:

```bash
02-agent-toolkit-mcp/scripts/run_checks.sh
```

The current checks verify expected scaffold files, validate shell script syntax
and print the Project 2 structure.

## Prompt and Command Helpers

Preview a Codex prompt template:

```bash
./scripts/run_codex_prompt.sh review-workflow
```

Preview a Claude Code command template:

```bash
./scripts/run_claude_command.sh review-workflow
```

These scripts do not invoke Codex, Claude Code or external services. They are
scaffold helpers for reviewers and future development.

## Safety Defaults

- Do not hardcode secrets.
- Do not add real external credentials.
- Do not perform destructive actions without explicit approval.
- Validate inputs before future MCP tools execute operations.
- Preserve auditability through clear inputs, outputs and logs.
- Keep README and handoff documentation current for every milestone.

## Next Milestone

Project 2 Milestone 2 should implement the initial MCP server scaffold and
deterministic local tools without adding real external integrations.

