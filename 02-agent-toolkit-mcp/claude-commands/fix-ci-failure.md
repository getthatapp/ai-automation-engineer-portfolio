# fix-ci-failure

Purpose: investigate and repair CI failures with the smallest safe change.

## Inputs

- Failing CI job or command.
- Relevant CI workflow file.
- Local reproduction command, if available.

## Command Instructions

1. Read `CLAUDE.md` and relevant project guidance.
2. Inspect the failing job and command.
3. Reproduce locally when practical.
4. Identify the root cause.
5. Apply the smallest scoped fix.
6. Re-run the relevant verification commands.

## Safety Constraints

- Do not hardcode secrets.
- Do not bypass or weaken checks without explicit approval.
- Do not modify unrelated projects.
- Do not perform destructive cleanup without approval.

## Expected Output

- Root cause.
- Files changed.
- Verification commands and results.
- Residual risk.

