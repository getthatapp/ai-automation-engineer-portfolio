# review-workflow

Purpose: review an agentic automation workflow for correctness, safety and
operational readiness.

## Inputs

- Workflow path or project directory.
- Relevant README, architecture and safety documentation.
- Test and CI commands, if available.

## Command Instructions

1. Read `CLAUDE.md` and relevant project guidance.
2. Inspect workflow boundaries, deterministic logic and external-call surfaces.
3. Check for input validation, timeout handling, secret safety and approval
   checkpoints.
4. Review observability, generated artifacts and test coverage.
5. Return findings ordered by severity with file references when possible.

## Safety Constraints

- Do not modify files unless explicitly asked.
- Do not run destructive commands.
- Do not call real external services.

## Expected Output

- Critical findings.
- Non-blocking improvements.
- Test gaps.
- Verification performed.

