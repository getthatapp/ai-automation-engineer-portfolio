# Architecture

Project 2 is a dual-agent toolkit scaffold. It is designed to support Codex and
Claude Code workflows without coupling the toolkit to one agent interface.

## Layers

```text
Codex prompts          Claude Code commands
        \              /
         shared skills
              |
     local adapter scripts
              |
       MCP tools
              |
 deterministic local operations
```

## Codex Layer

Codex workflows use `AGENTS.md`-oriented guidance and explicit prompt files.
Prompts should define the goal, current state, constraints, implementation
scope and verification commands.

Milestone 3 adds Project 1 review prompts for runtime inspection, report review
and demo-readiness summaries. These prompts tell Codex to use deterministic
local tool outputs as evidence and avoid inventing missing artifact data.

## Claude Code Layer

Claude Code workflows use `CLAUDE.md`-oriented guidance plus command templates.
Future milestones may add hooks and command wrappers, but this scaffold only
contains reusable command documentation.

Milestone 3 adds matching command templates for the same Project 1 review
flows. They are framed for Claude Code usage but still rely on local scripts and
deterministic tool output rather than external services.

## Local Adapter Script Layer

The scripts under `scripts/` provide practical read-only entrypoints for agent
workflows:

- `demo_mcp_tools.sh` previews the local tool registry and Project 1 demo
  readiness checks.
- `run_project1_tool_review.sh` runs report, run-history, approval and runtime
  checks against Project 1 paths.

These scripts do not delete runtime files, mutate Project 1, call external APIs
or require secrets. They are local adapters around the deterministic Python tool
package, not external MCP client integrations.

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

Milestone 3 does not add external service integrations, notification providers,
destructive tools, cloud deployment, frontend UI or live external MCP transport
integration. The MCP tool layer and adapter scripts are local, read-only and
deterministic.
