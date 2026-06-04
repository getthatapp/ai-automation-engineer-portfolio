# Project 2 Case Study: Agent Toolkit for Codex and Claude Code

## Problem

AI automation work often becomes hard to review because prompts, local tools,
permissions, verification commands and safety expectations live in separate
places. Project 1 demonstrates a working marketing operations automation
workflow, but a reviewer still needs a practical way to inspect its generated
reports, run history and approval artifacts without writing Python or trusting
an LLM summary.

Project 2 solves that portfolio problem by packaging reusable agent workflow
assets around deterministic local tools.

## Goal

Project 2 provides a local, reviewer-friendly toolkit for Codex and Claude Code
workflows. It demonstrates how an AI automation engineer can combine:

- reusable prompt and command workflows;
- deterministic MCP-style tool functions;
- typed local Python package structure;
- a command-line interface for tool invocation;
- permission profile documentation;
- CI and local verification;
- guardrail and hook examples.

The project is intentionally local-only. It does not deploy a real external MCP
service, call external APIs, require secrets or implement destructive tools.

## Architecture

Project 2 is organized as a layered toolkit:

```text
Codex prompts          Claude Code commands
        \              /
         shared skills
              |
    hooks and guardrail examples
              |
 runtime permission docs
              |
    CI and local quality checks
              |
     local adapter scripts
              |
          local CLI
              |
       MCP-style tools
              |
 deterministic local operations
```

The lowest layer inspects Project 1 artifacts from disk. Higher layers make
those checks usable from shell scripts, Codex prompts, Claude Code command
templates, guardrail examples and reviewer documentation.

## Key Design Decisions

- Keep tool behavior deterministic and read-only.
- Inspect Project 1 artifacts instead of changing Project 1 runtime behavior.
- Use Pydantic models and explicit path-safety helpers for local tool inputs
  and outputs.
- Expose tools through both Python functions and the `agent-toolkit-mcp` CLI.
- Treat Codex and Claude Code as related but different agent surfaces.
- Use documentation and scripts for local permission boundaries instead of
  claiming runtime-enforced policy.
- Keep CI credential-free and limited to local checks.

## Codex Support

Codex support is centered on `AGENTS.md`, reusable prompt templates and
hook-equivalent guardrail wrappers.

Relevant evidence:

- `codex-prompts/` contains reusable review and implementation prompts.
- `scripts/run_codex_prompt.sh` previews prompt templates without invoking
  Codex or external services.
- `hooks/codex/` contains preflight, post-run audit and prompt-history wrapper
  examples.
- `docs/CODEX_USAGE.md` and `docs/CODEX_HOOK_EQUIVALENTS.md` document expected
  local workflows.

Codex does not have Claude Code hook lifecycle parity in this project. The
Codex examples are guardrail wrappers and workflow conventions.

## Claude Code Support

Claude Code support is centered on `CLAUDE.md`, reusable command templates and
hook-style example scripts.

Relevant evidence:

- `claude-commands/` contains command templates matching the Codex review
  flows.
- `scripts/run_claude_command.sh` previews command templates without invoking
  Claude Code or external services.
- `hooks/claude-code/` contains example pre-tool, post-tool and runtime-clean
  hook scripts.
- `docs/CLAUDE_CODE_USAGE.md` and `docs/CLAUDE_CODE_HOOKS.md` document how the
  examples fit Claude Code-style workflows.

The hook examples are local examples, not a complete security system.

## Deterministic MCP/Tool Layer

The local MCP-style package lives under `mcp-server/`. It exposes deterministic
tool functions for inspecting Project 1 artifacts:

- `validate_report`
- `read_run_history`
- `list_pending_approvals`
- `check_runtime_clean`
- `generate_demo_brief`

The tools read local files, validate structure, sanitize sensitive-looking
output where applicable and return structured evidence. They do not call an
LLM, call external APIs, require credentials, delete files or mutate Project 1
artifacts.

## CLI Interface

The package exposes the `agent-toolkit-mcp` console script so reviewers can run
the deterministic tools without writing Python:

```bash
cd 02-agent-toolkit-mcp/mcp-server
uv run agent-toolkit-mcp --help
uv run agent-toolkit-mcp generate-demo-brief ../../01-ai-marketing-ops-agent --pretty
uv run agent-toolkit-mcp check-runtime-clean ../../01-ai-marketing-ops-agent --pretty
```

The CLI prints JSON evidence and returns non-zero status codes for validation
failures, dirty runtime checks, invalid paths and malformed inputs.

## Runtime Permission Profiles

Runtime docs define local operating profiles for Codex and Claude Code:

- read-only review;
- workspace-write development;
- approval-required operations;
- blocked destructive operations.

These profiles are documentation and workflow guidance. They do not claim a
deployed policy engine or external MCP runtime enforcement.

## Guardrails and Hook Examples

Project 2 includes local guardrail examples under `hooks/`:

- shared checks for prompt-history structure, runtime cleanliness and obvious
  secret-like patterns;
- Codex preflight and post-run wrapper examples;
- Claude Code hook-style pre-tool, post-tool and runtime-clean examples.

The scripts are deterministic, read-only and local-only. They intentionally
avoid deleting runtime files, mutating source code, requiring secrets or
calling external APIs. They are examples and should not be treated as complete
security enforcement.

## Testing and CI

Project 2 includes both local and GitHub Actions verification:

- scaffold checks with `scripts/run_checks.sh`;
- MCP server tests, linting and typing with `scripts/run_mcp_checks.sh`;
- local CI mirror with `scripts/run_ci_locally.sh`;
- guardrail checks with `scripts/run_guardrail_checks.sh`;
- GitHub Actions workflow in `.github/workflows/project-2-ci.yml`.

CI runs local deterministic checks only. It does not call external APIs, require
secrets, deploy anything, publish packages, run Docker services or mutate
Project 1 runtime artifacts.

## How to Run Locally

From the repository root:

```bash
02-agent-toolkit-mcp/scripts/run_checks.sh
02-agent-toolkit-mcp/scripts/run_mcp_checks.sh
02-agent-toolkit-mcp/scripts/run_ci_locally.sh
02-agent-toolkit-mcp/scripts/run_guardrail_checks.sh
```

From the MCP server package:

```bash
cd 02-agent-toolkit-mcp/mcp-server
uv run pytest
uv run ruff check .
uv run mypy src
uv run agent-toolkit-mcp generate-demo-brief ../../01-ai-marketing-ops-agent --pretty
```

## What This Demonstrates

Project 2 demonstrates production-oriented agent tooling rather than a chatbot:

- local MCP-style tool design;
- typed and testable Python package structure;
- safe local artifact inspection;
- CLI ergonomics for reviewers;
- dual-agent workflow support;
- prompt and command reuse;
- permission profile documentation;
- hook and guardrail examples;
- CI-backed quality checks;
- careful limitation-setting around external integration claims.

## Limitations / Next Steps

Current limitations:

- no deployed external MCP server;
- no external MCP client transport invocation from Codex or Claude Code;
- no real external integrations or secret-backed providers;
- no destructive or write-capable MCP tools;
- no complete security enforcement;
- no claim that Codex has the same lifecycle hook model as Claude Code.

Optional future enhancements could include richer packaged examples, more
guardrail templates, additional local tool functions or a later external MCP
transport layer if it remains credential-free and clearly documented.
