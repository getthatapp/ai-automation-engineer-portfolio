# Runbook Writer Skill

Use this skill when writing operational runbooks for automation workflows.

## Runbook Sections

- Purpose.
- Prerequisites.
- Environment variables.
- Setup commands.
- Run commands.
- Expected outputs.
- Inspection commands for logs, reports or run history.
- Cleanup commands.
- Common failure modes.
- Verification commands.

## Writing Rules

- Use commands that exist in the repository.
- Mark optional integrations clearly.
- Do not include real secrets.
- Keep the runbook concise and practical.
- Prefer reviewer-friendly local demo flows.

## Safety

Do not recommend destructive cleanup unless the command is clearly scoped and
the user has explicitly requested it.

