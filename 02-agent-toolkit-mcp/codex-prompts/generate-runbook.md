# Generate Runbook

Use this prompt with Codex to create or update a runbook for an automation
workflow.

```text
Read the relevant AGENTS.md files, README files and architecture docs first.

Task:
Generate or update a practical runbook for the workflow.

Include:
- prerequisites;
- environment variables and safe defaults;
- setup commands;
- local run commands;
- expected outputs;
- logs or run-history inspection;
- cleanup commands;
- known failure modes;
- verification commands.

Rules:
- Do not invent commands that do not exist.
- Do not include real secrets.
- Mark optional integrations clearly.
- Keep the runbook concise and reviewer-friendly.
- Do not change runtime behavior.

After implementation, summarize:
1. files changed,
2. runbook sections added,
3. verification performed.
```

