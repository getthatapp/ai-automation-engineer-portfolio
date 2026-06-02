# Fix CI Failure

Use this prompt with Codex to investigate and fix a CI failure.

```text
Read the relevant AGENTS.md files and CI configuration first.

Task:
Investigate the CI failure and implement the smallest safe fix.

Process:
- inspect the failing job and command;
- reproduce the failure locally when practical;
- identify whether the failure is code, test, config or environment related;
- make the smallest scoped fix;
- avoid unrelated refactors;
- update documentation if commands or behavior change.

Rules:
- Do not hardcode secrets.
- Do not bypass tests.
- Do not weaken type, lint or safety checks unless explicitly requested.
- Do not modify unrelated projects.

After implementation, summarize:
1. root cause,
2. files changed,
3. verification commands,
4. residual risk.
```

