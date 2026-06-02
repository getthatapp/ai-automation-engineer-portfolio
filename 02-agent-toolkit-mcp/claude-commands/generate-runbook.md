# generate-runbook

Purpose: generate or update a practical runbook for an automation workflow.

## Inputs

- Project README and architecture docs.
- Existing scripts and verification commands.
- Known runtime artifact locations.

## Command Instructions

1. Read `CLAUDE.md`, project README and architecture docs.
2. Identify setup, run, inspection, cleanup and verification commands.
3. Document required environment variables and safe local defaults.
4. Describe expected outputs and common failure modes.
5. Keep the result concise and reviewer-friendly.

## Safety Constraints

- Do not invent commands.
- Do not include real secrets.
- Do not change runtime behavior.
- Mark optional integrations clearly.

## Expected Output

- Files changed.
- Runbook sections added.
- Verification performed.

