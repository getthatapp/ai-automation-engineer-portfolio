# Architecture

Project 2 is a dual-agent toolkit scaffold. It is designed to support Codex and
Claude Code workflows without coupling the toolkit to one agent interface.

## Layers

```text
Codex prompts          Claude Code commands
        \              /
         shared skills
              |
       MCP tools
              |
 deterministic local operations
```

## Codex Layer

Codex workflows use `AGENTS.md`-oriented guidance and explicit prompt files.
Prompts should define the goal, current state, constraints, implementation
scope and verification commands.

## Claude Code Layer

Claude Code workflows use `CLAUDE.md`-oriented guidance plus command templates.
Future milestones may add hooks and command wrappers, but this scaffold only
contains reusable command documentation.

## Shared Skill Layer

Shared skills describe repeatable engineering practices that can be used by
both Codex and Claude Code. They should stay practical, scoped and tied to
reviewable outputs.

## MCP Tool Layer

MCP tools should be deterministic. A tool should have clear inputs, validation,
bounded side effects, safe errors and auditable outputs. Tools should not hide
business reasoning inside vague LLM prompts.

The first implementation is a Python package under `mcp-server/`. The package
uses Pydantic schemas and direct Python functions for the deterministic tool
logic. `server.py` currently provides a minimal local registry for tool
discovery and invocation; full external MCP SDK transport wiring is intentionally
left for a later milestone.

Current tools inspect Project 1 local artifacts:

- Markdown report section validation.
- Workflow run JSONL inspection.
- Pending approval JSONL inspection.
- Runtime artifact cleanliness checks.
- Deterministic Project 1 demo readiness briefs.

## Milestone Boundary

This milestone does not add external service integrations, notification
providers, destructive tools, cloud deployment or frontend UI. The MCP tool
layer is local, read-only and deterministic.
