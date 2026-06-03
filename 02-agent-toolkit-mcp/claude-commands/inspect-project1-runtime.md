# Inspect Project 1 Runtime

## Purpose

Use Project 2 deterministic local tools to inspect Project 1 runtime artifacts
from Claude Code without mutating Project 1.

## Expected Inputs

- Project 1 path: `01-ai-marketing-ops-agent`
- Optional explicit report path.

## Command Steps

1. Read `CLAUDE.md`, `AGENTS.md` and the Project 2 usage docs.
2. Run:

   ```bash
   02-agent-toolkit-mcp/scripts/run_project1_tool_review.sh
   ```

3. Base the review only on outputs from `check_runtime_clean`,
   `read_run_history`, `list_pending_approvals` and optional `validate_report`.
4. Report missing artifacts as missing evidence.

## Safety Constraints

- Read-only only.
- Do not delete Project 1 runtime files.
- Do not call external APIs.
- Do not require secrets.
- Do not claim external MCP client invocation unless it has been implemented and
  verified.

## Review Checklist

- Runtime artifact paths are listed.
- Pending approvals are interpreted as review items.
- Run history is summarized only when present.
- Missing files are not treated as proof of success or failure.
