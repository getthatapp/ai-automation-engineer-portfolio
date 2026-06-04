# Project 3 Technical Defense

Project 3 is AgentOps Control Tower. Its current status is local summaries and
timeline ready. The core defense is that it aggregates local evidence from
Projects 1 and 2 into deterministic ingestion, summary and timeline models
without claiming a dashboard, database or deployed AgentOps platform.

## Milestone 1 — AgentOps Control Tower Scaffold

### What was built

The initial `03-agentops-control-tower/` scaffold was created with README,
`AGENTS.md`, architecture, roadmap, observability model, data source, safety
model, local demo plan, prompt-history files, example evidence docs and a local
scaffold check script.

### Why this milestone existed

Engineering-wise, it defined the responsibilities of the AgentOps layer before
adding ingestion code. Portfolio-wise, it connected the first two projects into
a broader operational story: workflow execution, local tool evidence and
observability.

### What the prompt enforced

The prompt enforced scaffold-only scope, no backend ingestion yet, no frontend
UI, no external integrations, no secrets, no Project 1 code changes, no Project
2 code changes except documentation links if needed, no package dependencies,
no external API calls and no overclaiming.

### Key technical decisions

The project was framed as local-first and evidence-oriented. It was not
positioned as a workflow runner or a replacement for Projects 1 and 2.

### How to defend it in an interview

Say: "Project 3 starts as the observability layer. Milestone 1 deliberately
defined the architecture, data sources and safety boundaries before writing
ingestion logic, so the scope stayed clear."

### Likely recruiter questions

- Why start a third project?
- Did this milestone implement a dashboard?
- What does AgentOps mean here?

### Strong answers

- Project 1 produces workflow artifacts and Project 2 produces tool evidence;
  Project 3 observes those signals.
- No. Milestone 1 was scaffold and documentation only.
- It means local workflow health, approvals, failures, guardrails and audit
  signals, not a deployed commercial platform.

### Verification evidence

Recorded verification included `03-agentops-control-tower/scripts/run_checks.sh`
passing, Bash script syntax passing and `git diff --check` passing.

### Limitations

No backend ingestion, Python package logic, UI, dashboard, database, scheduler,
external API or deployed AgentOps service existed in this milestone.

### What came next

Milestone 2 added local typed ingestion models and parsers.

## Milestone 2 — Local Data Ingestion Models

### What was built

A Python package was added under `src/agentops_control_tower/` with Pydantic
ingestion models for workflow runs, approval requests, report summaries, tool
evidence, guardrail evidence, warnings and errors. Deterministic parsers were
added for Project 1 run-history JSONL, approval request JSONL and Markdown
reports, plus saved Project 2 CLI JSON evidence and guardrail output text.
Conservative recursive redaction was added for secret-like keys and values.

### Why this milestone existed

Engineering-wise, it converted local artifacts into typed records that can
support later summaries or dashboards. Portfolio-wise, it showed AgentOps work
as concrete parsing, validation and sanitization rather than vague monitoring
claims.

### What the prompt enforced

The prompt enforced no Project 1 or Project 2 runtime behavior changes, no
frontend UI, no external integrations, no external API calls, no secrets, no
file mutation, no secret values in errors, no generated runtime deletion and no
overclaiming of dashboards, databases, schedulers or deployed AgentOps
platforms.

### Key technical decisions

Ingestion is local and read-only. Missing optional files produce warnings;
malformed files produce explicit ingestion errors. Parsed payloads are
sanitized before being stored in internal records.

### How to defend it in an interview

Say: "Milestone 2 implemented the evidence ingestion boundary. It reads local
artifacts from Projects 1 and 2, validates them into typed records and reports
warnings or errors deterministically."

### Likely recruiter questions

- What artifacts can Project 3 ingest?
- Does it modify Project 1 or Project 2 files?
- How are secrets handled?

### Strong answers

- Project 1 run history, approval requests and Markdown reports, plus saved
  Project 2 CLI JSON and guardrail text.
- No. It is read-only.
- It uses conservative redaction for secret-like keys and values and avoids
  printing secret values in errors.

### Verification evidence

Recorded verification included Project 3 checks passing with 16 tests, ruff
clean, mypy clean and `git diff --check` clean; Bash syntax passing; direct
pytest, ruff and mypy passing; and the ingestion demo passing with
`records=4`, `warnings=0`, `errors=0`, `ok=true`.

### Limitations

The milestone did not add summaries, timeline generation, UI, dashboard,
database, scheduler or external integrations.

### What came next

Milestone 3 added deterministic local summaries and timeline generation over
ingested records.

## Milestone 3 — Local AgentOps Summaries and Timeline

### What was built

Timeline and summary models were added, along with deterministic timeline
generation, summary generation and combined control tower view creation. The
project now produces dashboard-ready summary counts, health status,
recommended local follow-up actions and a deterministic AgentOps timeline over
typed ingestion results.

### Why this milestone existed

Engineering-wise, it turned parsed evidence into operational views. Portfolio-
wise, it demonstrated the beginning of an AgentOps control layer without
pretending a UI or deployed platform exists.

### What the prompt enforced

The prompt enforced no Project 1 or Project 2 runtime behavior changes, no
frontend UI, no external integrations, no external API calls, no secrets, no
database or scheduler, no timestamp inference, no LLM calls, no file mutation,
no generated runtime deletion and no deployed AgentOps overclaims.

### Key technical decisions

Overall health is derived deterministically: ingestion errors produce `error`;
failed or blocked guardrails, pending approvals, failed workflow runs or
human-review report signals produce `needs_attention`; warnings or unknown
statuses produce `warning`; otherwise the view is `healthy`. Recommended
actions are deterministic local follow-ups, not LLM recommendations.

### How to defend it in an interview

Say: "Milestone 3 is the first control-tower view. It does not render a
dashboard yet, but it produces the typed summary and timeline data a dashboard
or CLI export could consume."

### Likely recruiter questions

- Is there a dashboard now?
- How is health status calculated?
- Does it use an LLM for recommendations?

### Strong answers

- No. It creates local summary and timeline models only.
- Health status is derived by deterministic rules from errors, warnings,
  guardrails, approvals, workflow statuses and report signals.
- No. Recommended actions are deterministic follow-ups based on local records.

### Verification evidence

Recorded verification included Project 3 checks passing with 33 tests, ruff
clean, mypy clean and `git diff --check` clean; ingestion demo passing;
summary demo passing with `overall_status=needs_attention` and
`timeline_events=4`; Bash syntax passing; direct pytest, ruff and mypy passing.

### Limitations

Project 3 still does not implement a UI, dashboard, database persistence,
scheduler, background service, external integrations, notification providers or
deployed AgentOps service.

### What came next

The next planned milestone is local report export or a dashboard-ready CLI.

