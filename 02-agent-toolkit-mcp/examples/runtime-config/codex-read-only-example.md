# Codex Read-Only Example

Use this profile when Codex should inspect Project 2 docs or Project 1
artifacts without changing files.

## Profile

Read-only inspection.

## Example Workflow

```bash
02-agent-toolkit-mcp/scripts/show_permission_profiles.sh
02-agent-toolkit-mcp/scripts/demo_mcp_tools.sh
02-agent-toolkit-mcp/scripts/run_project1_tool_review.sh
02-agent-toolkit-mcp/scripts/run_codex_prompt.sh inspect-project1-runtime
```

## Codex Instructions

- Use deterministic local outputs as evidence.
- Do not edit Project 1.
- Do not delete runtime artifacts.
- Do not call external APIs.
- Treat missing files as missing evidence.

## Not Included

- Real credentials.
- External MCP deployment.
- Destructive operations.
