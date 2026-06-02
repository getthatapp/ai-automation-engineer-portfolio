# Project 1 Demo Script

This script is designed for a 5-10 minute walkthrough of Project 1: AI
Marketing Operations Agent.

## 1. Opening: Project Goal

What to say:

> This project is an AI automation engineering case study. It is not a chatbot.
> It automates a daily marketing operations workflow across a browser-only
> panel, REST API, GraphQL API, deterministic validation, anomaly detection,
> reporting, observability, optional LLM interpretation, human approval and
> approval-aware mock notifications.

Show:

- root `README.md`;
- `docs/PROJECT_1_CASE_STUDY.md`;
- `docs/REQUIREMENTS_COVERAGE_MATRIX.md`.

Key point:

- The system is local and reviewer-safe. It does not require real credentials
  or real external notification providers.

## 2. Architecture Overview

Show:

- `01-ai-marketing-ops-agent/docs/ARCHITECTURE.md`;
- the pipeline in root `README.md`;
- source directories under `01-ai-marketing-ops-agent/src/marketing_ops_agent/`.

What to say:

> The workflow uses APIs where APIs exist and Playwright only for the local
> mock panel because that surface deliberately has no API. Data is aggregated
> into typed `CampaignSnapshot` objects before anomaly detection, reporting or
> LLM interpretation.

Call out:

- `browser/` for Playwright scraping;
- `clients/` for REST and GraphQL integrations;
- `aggregation/` for deterministic source joining;
- `anomaly/` for rule-based findings;
- `reporting/` for deterministic Markdown output;
- `workflows/` for orchestration;
- `approval/`, `observability/`, `llm/`, `notifications/` for operational layers.

## 3. Local Run Steps

From the repository root:

```bash
cd 01-ai-marketing-ops-agent
uv sync
uv run playwright install chromium
./scripts/start_services.sh
```

Then run the deterministic workflow:

```bash
./scripts/run_workflow.sh
```

What to say:

> The scripts exist so a reviewer can run the demo without relying on my shell
> aliases. They use local mock credentials by default and allow environment
> variables to override them.

Default mock panel credentials:

```text
MARKETING_PANEL_USERNAME=demo@example.com
MARKETING_PANEL_PASSWORD=local-password
MARKETING_PANEL_2FA_CODE=000000
```

## 4. Expected Outputs

After a workflow run, show:

```bash
ls -lt reports/
tail -n 5 run-history/workflow-runs.jsonl
tail -n 20 approval-requests/approval-requests.jsonl
```

What to say:

> The workflow writes runtime artifacts locally. Reports, run history and
> approval records are intentionally ignored by git.

Expected runtime paths:

- `reports/` for Markdown reports;
- `run-history/workflow-runs.jsonl` for workflow observability;
- `approval-requests/approval-requests.jsonl` when approval requests exist.

## 5. Report Inspection

Open the latest report:

```bash
sed -n '1,220p' "$(ls -t reports/*.md | head -n 1)"
```

What to show:

- executive summary;
- campaign health overview;
- critical and warning anomalies;
- grouped Data Quality Issues section;
- Human Review Required section;
- campaign snapshot table;
- deterministic recommended actions;
- limitations / missing data.

What to say:

> The report is deterministic. It is generated from `CampaignSnapshot` and
> `AnomalyFinding` objects only. It does not consume raw scraped rows, raw REST
> payloads or raw GraphQL payloads, and it does not ask an LLM to invent missing
> metrics.

## 6. Run-History Inspection

Show:

```bash
tail -n 5 run-history/workflow-runs.jsonl
```

What to say:

> Each workflow run records a structured JSONL summary with status, timestamps,
> report path, snapshot and finding counts, approval request count, optional
> notification status and sanitized failure information.

Point out:

- run ID;
- status such as `succeeded` or `needs_approval`;
- report path;
- finding counts;
- approval request count;
- data quality summary.

## 7. Approval Request Inspection

Show when present:

```bash
tail -n 20 approval-requests/approval-requests.jsonl
```

What to say:

> Critical findings, human-review findings and high-risk LLM recommendations
> create pending approval requests. Pending approvals are not approved actions.
> This is the guardrail before any sensitive external action.

Important language:

- Pending means waiting for human review.
- The workflow can complete while still requiring approval.
- High-risk outputs are never auto-approved.

## 8. Optional LLM Interpretation

Run:

```bash
./scripts/run_workflow_with_llm.sh
```

What to say:

> The LLM layer is optional and downstream of deterministic validation. It
> receives validated snapshots, deterministic findings and report text. It does
> not scrape, join, validate, calculate metrics or replace deterministic
> findings. Local runs use a deterministic mock provider by default.

Show:

- `01-ai-marketing-ops-agent/src/marketing_ops_agent/llm/`;
- LLM prompt safety rules if time allows.

## 9. Approval-Aware Notification Behavior

Run:

```bash
NOTIFICATION_DELIVERY_ENABLED=true ./scripts/run_workflow.sh
```

What to say:

> Notification delivery is optional and uses a deterministic mock provider in
> this project. It does not call Slack, Telegram, email or any external API.
> The notification is summary-only and includes pending approval IDs when they
> exist. It explicitly says pending approvals are not approved actions.

Show:

- `01-ai-marketing-ops-agent/src/marketing_ops_agent/notifications/`;
- run-history notification status when available.

## 10. CI/CD Checks

Show:

- `.github/workflows/project-1-ci.yml`;
- `01-ai-marketing-ops-agent/scripts/run_ci_locally.sh`.

Run locally if time allows:

```bash
./scripts/run_ci_locally.sh
```

What to say:

> CI runs the same core checks a reviewer can run locally: dependency sync,
> Playwright Chromium install, pytest, ruff, mypy, Docker Compose config
> validation and Bash syntax checks. CI does not require secrets and does not
> call real external APIs.

## 11. Closing Talking Points

Use these points to close:

- The project demonstrates controlled AI automation, not chatbot wrapping.
- Deterministic code owns scraping, validation, metrics, anomaly detection,
  persistence and reporting.
- LLM use is optional, downstream and bounded.
- Human approval gates protect sensitive actions.
- Notifications are approval-aware and mocked locally.
- The system is testable, documented and CI-validated.
- Project 2 is planned next: MCP Automation Server + Claude Code Toolkit.
