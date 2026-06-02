# Agent Toolkit MCP Server

This package contains the first deterministic local MCP tool layer for Project
2. It is intentionally lightweight: the tool logic is plain Python with typed
Pydantic inputs and outputs, and the current server module exposes a minimal
registry for local discovery and invocation.

The package does not call external APIs, require secrets, mutate Project 1
artifacts or implement destructive tools.

## Tools

- `validate_report(report_path)`: validates required sections in a Project 1
  Markdown report.
- `read_run_history(jsonl_path, limit=5)`: returns recent sanitized workflow
  run records from JSONL.
- `list_pending_approvals(jsonl_path)`: returns sanitized pending approval
  summaries from JSONL.
- `check_runtime_clean(project_path)`: reports generated runtime files such as
  reports, run history, approval queue files, `__pycache__/` and `*.pyc`.
- `generate_demo_brief(project_path)`: creates a deterministic local-only
  Project 1 demo readiness summary.

## Local Checks

From this directory:

```bash
uv run pytest
uv run ruff check .
uv run mypy src
```

From the repository root:

```bash
02-agent-toolkit-mcp/scripts/run_mcp_checks.sh
```

## Manual Registry Inspection

```bash
uv run python -m agent_toolkit_mcp.server
```

This prints the registered local tool names and descriptions. It does not start
a network service or call an external MCP client.
