# Review Workflow

Use this prompt with Codex to review an agentic automation workflow.

```text
Read the relevant AGENTS.md files and project documentation first.

Task:
Review the workflow implementation for correctness, safety and maintainability.

Focus on:
- deterministic boundaries;
- API vs browser automation choices;
- input validation;
- timeout and error handling;
- secret handling;
- approval checkpoints for risky actions;
- observability and auditability;
- test coverage and verification commands.

Rules:
- Do not change code unless explicitly asked.
- Do not run destructive commands.
- Do not call real external services.
- Lead with findings ordered by severity.
- Include file and line references when possible.

After review, summarize:
1. critical findings,
2. non-blocking improvements,
3. test gaps,
4. verification performed.
```

