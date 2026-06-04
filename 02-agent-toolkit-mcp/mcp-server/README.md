# Agent Toolkit MCP Server

This package contains the first deterministic local MCP tool layer for Project
2. It is intentionally lightweight: the tool logic is plain Python with typed
Pydantic inputs and outputs, and the current server module exposes a minimal
registry for local discovery and invocation.

The package does not call external APIs, require secrets, mutate Project 1
artifacts or implement destructive tools.

## Tools

- `validate_report(report_path)`: validates required sections in a Project 1
  Markdown report, extracts explicit summary values and reports non-fatal
  warnings such as empty content, missing generated timestamp or duplicate
  required headings.
- `read_run_history(jsonl_path, limit=5)`: returns recent sanitized workflow
  run records from JSONL with total valid record count and explicit malformed
  line reporting.
- `list_pending_approvals(jsonl_path)`: returns sanitized pending approval
  summaries from JSONL with total and pending record counts.
- `check_runtime_clean(project_path)`: reports generated runtime files such as
  reports, run history, approval queue files, `__pycache__/` and `*.pyc`, plus
  deterministic counts by artifact type.
- `generate_demo_brief(project_path)`: creates a deterministic local-only
  Project 1 demo readiness summary with a structured readiness checklist.

## Hardening Notes

- Inputs use Pydantic validation and explicit path checks.
- Symlinks are resolved before file, directory and child-path validation.
- Project-level runtime checks reject symlink matches that resolve outside the
  inspected project path.
- Secret-like JSON keys and obvious bearer/API-token values are redacted before
  records are returned to an agent.
- Tools report generated files; they never delete or mutate them.

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

## CLI Usage

Run local tools through the package console script:

```bash
uv run agent-toolkit-mcp validate-report ../../01-ai-marketing-ops-agent/reports/example.md
uv run agent-toolkit-mcp read-run-history ../../01-ai-marketing-ops-agent/run-history/workflow-runs.jsonl --limit 5
uv run agent-toolkit-mcp list-pending-approvals ../../01-ai-marketing-ops-agent/approval-requests/approval-requests.jsonl
uv run agent-toolkit-mcp check-runtime-clean ../../01-ai-marketing-ops-agent
uv run agent-toolkit-mcp generate-demo-brief ../../01-ai-marketing-ops-agent --pretty
```

Default output is compact JSON. `--pretty` may be passed before or after the
subcommand to print indented JSON.

Exit codes are intended for local status checks:

- `validate-report`: zero only when `valid=true`.
- `check-runtime-clean`: zero only when `clean=true`.
- `read-run-history`: zero for readable files and handled missing-file
  evidence; non-zero for malformed JSONL, invalid paths or invalid limits.
- `list-pending-approvals`: zero for readable files and handled missing-file
  evidence; non-zero for malformed JSONL or invalid paths.
- `generate-demo-brief`: zero only when the expected demo-readiness structure
  is present.

## Manual Registry Inspection

```bash
uv run python -m agent_toolkit_mcp.server
```

This prints the registered local tool names and descriptions. It does not start
a network service or call an external MCP client.
