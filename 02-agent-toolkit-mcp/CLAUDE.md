# CLAUDE.md

## Project Purpose

This project is the Agent Toolkit for Codex and Claude Code. Claude Code should
use this file as project-local guidance when working inside
`02-agent-toolkit-mcp/`.

## Claude Code Workflow

- Use `claude-commands/` for reusable command templates.
- Use `skills/` for shared task guidance.
- Keep command outputs auditable and reviewer-friendly.
- Do not claim that MCP runtime features exist until they are implemented.
- Do not modify Project 1 code unless explicitly requested.

## Safety Rules

- Do not hardcode secrets or credentials.
- Do not add real external integrations during scaffold work.
- Do not run destructive shell commands without explicit approval.
- Validate inputs for future tools and scripts.
- Keep documentation in English.

## Documentation Rules

- Update this README-level guidance when Claude Code workflows change.
- Update `README.md` and the portfolio handoff for every milestone.
- Keep verification commands explicit in summaries.

