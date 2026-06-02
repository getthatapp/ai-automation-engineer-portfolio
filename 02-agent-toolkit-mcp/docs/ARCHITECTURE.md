# Architecture

Project 2 is a dual-agent toolkit scaffold. It is designed to support Codex and
Claude Code workflows without coupling the toolkit to one agent interface.

## Layers

```text
Codex prompts          Claude Code commands
        \              /
         shared skills
              |
       future MCP tools
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

## Future MCP Tool Layer

MCP tools should be deterministic. A tool should have clear inputs, validation,
bounded side effects, safe errors and auditable outputs. Tools should not hide
business reasoning inside vague LLM prompts.

## Scaffold Boundary

This milestone does not implement an MCP server, register tools, add
dependencies or call external services. It establishes the documentation and
folder structure for later implementation.

