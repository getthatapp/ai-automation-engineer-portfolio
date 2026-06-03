# MCP Server Local Example

This example documents the current local MCP-style runtime. It does not claim a
deployed external MCP server or external client transport.

## Local Registry Inspection

```bash
cd 02-agent-toolkit-mcp/mcp-server
uv run python -m agent_toolkit_mcp.server
```

## Local Verification

```bash
02-agent-toolkit-mcp/scripts/run_mcp_checks.sh
```

## Project 1 Artifact Review

```bash
02-agent-toolkit-mcp/scripts/demo_mcp_tools.sh
02-agent-toolkit-mcp/scripts/run_project1_tool_review.sh
```

## Boundaries

- Local filesystem only.
- Read-only Project 1 artifact inspection.
- No external APIs.
- No secrets.
- No destructive tools.
- No deployed MCP transport claim.
