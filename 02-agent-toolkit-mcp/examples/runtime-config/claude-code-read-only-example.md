# Claude Code Read-Only Example

Use this profile when Claude Code should inspect local artifacts through
Project 2 command templates and scripts.

## Profile

Read-only inspection.

## Example Workflow

```bash
02-agent-toolkit-mcp/scripts/show_permission_profiles.sh
02-agent-toolkit-mcp/scripts/run_project1_tool_review.sh
02-agent-toolkit-mcp/scripts/run_claude_command.sh review-project1-report
```

## Claude Code Instructions

- Use command templates as review guidance.
- Use deterministic local outputs as evidence.
- Do not mutate Project 1 artifacts.
- Do not claim external MCP client invocation.

## Not Included

- External services.
- Real credentials.
- File deletion.
