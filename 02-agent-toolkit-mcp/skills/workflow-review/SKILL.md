# Workflow Review Skill

Use this skill when reviewing an automation workflow for correctness, safety and
operational readiness.

## Review Focus

- Confirm deterministic logic handles scraping, API calls, validation,
  persistence and retries where applicable.
- Confirm LLM usage is downstream of validated inputs and does not replace
  deterministic results.
- Confirm risky actions require human approval.
- Confirm secrets are not hardcoded or written to logs.
- Confirm generated artifacts are ignored by git.
- Confirm verification commands are documented and runnable.

## Output Format

Lead with findings ordered by severity. Include file references when possible.
Then summarize test gaps, verification performed and residual risk.

## Safety

Do not modify code during review unless the user explicitly asks for fixes.
Do not call real external services or run destructive commands.

