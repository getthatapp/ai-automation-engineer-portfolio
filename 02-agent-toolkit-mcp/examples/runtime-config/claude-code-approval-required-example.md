# Claude Code Approval-Required Example

Use this profile when Claude Code needs an operation that should be gated by
explicit human approval.

## Profile

Approval-required operations.

## Example Operations

- Dependency resolution for `run_mcp_checks.sh` if local caches are missing.
- Branch or commit operations.
- Future elevated non-destructive local setup steps.

## Example Verification

```bash
02-agent-toolkit-mcp/scripts/run_mcp_checks.sh
git diff --check
```

## Claude Code Instructions

- Ask before elevated execution.
- Keep the approved scope narrow.
- Record why approval was needed.
- Do not use approval to add destructive operations or real external services.

## Not Included

- Hardcoded secrets.
- Destructive cleanup.
- Production deployment.
