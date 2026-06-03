# Runtime Troubleshooting

## Missing Project 1 Directory

If an adapter script reports that Project 1 is missing, confirm the repository
layout:

```bash
ls 01-ai-marketing-ops-agent
```

The scripts default to `01-ai-marketing-ops-agent` from the repository root.

## Missing Report, Run History Or Approval Queue

Missing runtime artifacts are missing evidence. They do not prove that the
workflow never ran.

Generate Project 1 artifacts from Project 1 when needed:

```bash
cd 01-ai-marketing-ops-agent
./scripts/run_workflow.sh
```

Do not create fake reports, run history or approval records for a review.

## Script Permission Errors

Project 2 scripts should be executable. Check permissions with:

```bash
ls -l 02-agent-toolkit-mcp/scripts
```

If a script is not executable during development, fix the script permission in
the Project 2 milestone that adds or updates it.

## Missing MCP Server Virtualenv

The adapter scripts use the local MCP server virtualenv when available. Run the
MCP checks to prepare or validate the environment:

```bash
02-agent-toolkit-mcp/scripts/run_mcp_checks.sh
```

If dependency resolution is blocked by the sandbox, rerun only with explicit
approval and record the reason in the milestone notes.

## `uv` Dependency Resolution

`run_mcp_checks.sh` may need to resolve Python build dependencies if the local
environment is incomplete. This is expected for verification, but runtime docs
and examples must not require real credentials or external service access.

## Interpreting Runtime Cleanliness

`check_runtime_clean` reports generated runtime artifacts. A non-clean result
means local generated files are present; it is not an error and the tool does
not delete them.

## Unsupported Claims

Do not claim the following unless a future milestone implements and verifies
them:

- deployed external MCP server;
- real Codex or Claude Code external tool invocation;
- real notification provider delivery;
- production deployment;
- approved actions from pending approval records.
