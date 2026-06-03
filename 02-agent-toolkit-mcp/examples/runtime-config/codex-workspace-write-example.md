# Codex Workspace-Write Example

Use this profile when Codex should update Project 2 files in a scoped
documentation or tooling milestone.

## Profile

Workspace-write development.

## Example Workflow

```bash
02-agent-toolkit-mcp/scripts/run_checks.sh
02-agent-toolkit-mcp/scripts/run_mcp_checks.sh
bash -n 02-agent-toolkit-mcp/scripts/*.sh
git diff --check
```

## Codex Instructions

- Keep edits scoped to Project 2 and portfolio handoff docs.
- Do not modify Project 1 code or runtime behavior.
- Do not add real credentials.
- Do not add external service integrations.
- Update prompt history for every Project 2 milestone.

## Not Included

- Secrets.
- Production deployment.
- Destructive tools.
