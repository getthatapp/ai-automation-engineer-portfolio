# Project 1 Case Study: AI Marketing Operations Agent

## Problem

Marketing operations work often spans several systems: an internal web panel,
REST APIs, GraphQL analytics, reporting tools, task tracking and manager
approvals. A useful automation system must collect and validate data across
those boundaries without inventing missing metrics, hiding source mismatches or
turning an LLM into the source of truth.

Project 1 models that problem in a local, portfolio-friendly environment. It is
not a chatbot demo. It is a production-style automation workflow with explicit
boundaries, deterministic validation, observability and human approval gates.

## Goal

Build a daily marketing operations workflow that:

- scrapes an HTML-only marketing panel with Playwright;
- enriches campaigns with Campaign REST API metadata;
- enriches campaigns with Analytics GraphQL metrics;
- aggregates all source data into typed `CampaignSnapshot` objects;
- detects anomalies with deterministic rules;
- writes a deterministic Markdown report;
- records each workflow run locally;
- optionally adds LLM interpretation downstream of validated outputs;
- creates local human approval requests for high-risk outputs;
- optionally sends an approval-aware summary through a deterministic mock notification provider.

The project is designed to be runnable locally by an external reviewer without
real credentials or external SaaS dependencies.

## Architecture

The workflow is intentionally layered:

```text
Mock marketing panel + REST API + GraphQL API
        ↓
Playwright scraper + typed service clients
        ↓
CampaignSnapshot with data quality flags
        ↓
Deterministic anomaly findings
        ↓
Deterministic Markdown report
        ↓
Workflow orchestration and local report output
        ↓
Optional LLM interpretation over validated outputs
        ↓
Human approval requests for high-risk outputs
        ↓
Optional approval-aware mock notification summary
        ↓
Persistent JSONL run history
```

Core modules live under:

- `01-ai-marketing-ops-agent/src/marketing_ops_agent/browser/`
- `01-ai-marketing-ops-agent/src/marketing_ops_agent/clients/`
- `01-ai-marketing-ops-agent/src/marketing_ops_agent/aggregation/`
- `01-ai-marketing-ops-agent/src/marketing_ops_agent/anomaly/`
- `01-ai-marketing-ops-agent/src/marketing_ops_agent/reporting/`
- `01-ai-marketing-ops-agent/src/marketing_ops_agent/workflows/`
- `01-ai-marketing-ops-agent/src/marketing_ops_agent/observability/`
- `01-ai-marketing-ops-agent/src/marketing_ops_agent/approval/`
- `01-ai-marketing-ops-agent/src/marketing_ops_agent/llm/`
- `01-ai-marketing-ops-agent/src/marketing_ops_agent/notifications/`

## Key Design Decisions

- Use APIs when APIs exist. Campaign REST and Analytics GraphQL data are
  collected through typed `httpx` clients.
- Use Playwright only where no API exists. The local marketing panel is
  deliberately HTML-only.
- Keep aggregation deterministic. `CampaignSnapshot` stores panel, REST and
  GraphQL values separately so source disagreements remain visible.
- Detect anomalies with explicit Python rules before any LLM step.
- Generate the baseline report deterministically from snapshots and findings.
- Keep LLM interpretation optional and downstream. It may summarize and
  recommend, but it must not scrape, validate, calculate or replace findings.
- Require human approval for critical findings, human-review flags and
  high-risk LLM recommendations.
- Treat pending approvals as pending. They are not approved actions.
- Keep notifications mock and optional. Real Slack, Telegram and email
  providers are not implemented in Project 1.
- Persist run history and approvals locally as JSONL for auditability.

## End-to-End Workflow

1. Start local FastAPI mock services with Docker Compose.
2. Scrape campaign rows from the mock marketing panel using Playwright.
3. Fetch matching campaign metadata from the Campaign REST API.
4. Fetch matching metrics from the Analytics GraphQL API.
5. Aggregate source records into `CampaignSnapshot` objects.
6. Attach data quality flags and human-review signals when sources are missing,
   stale or inconsistent.
7. Detect deterministic anomalies such as high spend with low conversions,
   CPA above threshold, negative ROI and data quality findings.
8. Render a deterministic Markdown report under `reports/`.
9. Optionally run deterministic mock LLM interpretation over validated outputs.
10. Create local approval requests for sensitive or high-risk outputs.
11. Optionally send a summary-only mock notification that includes pending
    approval request IDs.
12. Append a structured JSONL run record under `run-history/`.

## Guardrails

- No real CAPTCHA bypass logic.
- No hardcoded real secrets.
- `.env.example` contains local mock defaults and empty placeholders only.
- Generated reports, run history and approval records are ignored by git.
- External calls have timeout and error handling boundaries.
- Partial source data is represented through data quality flags, not silently
  dropped or inferred.
- Missing metrics are shown as `missing`.
- LLM prompts consume only validated deterministic outputs.
- LLM output is not the source of truth for anomaly counts, workflow status or
  data quality flags.
- Pending approval requests are never treated as approved actions.
- Notification delivery uses a deterministic mock provider in this project.

## Testing and CI

Project 1 includes automated coverage for the workflow layers, including:

- retry and rate limiter utilities;
- Pydantic domain models;
- mock FastAPI services;
- typed REST and GraphQL clients;
- Playwright scraper behavior through fakes;
- aggregation and data quality flags;
- deterministic anomaly detection;
- Markdown report rendering;
- workflow orchestration;
- local run recording;
- optional LLM interpretation;
- approval flow;
- approval-aware notification behavior.

GitHub Actions CI runs from `01-ai-marketing-ops-agent` and validates:

- `uv sync`;
- `uv run playwright install chromium`;
- `uv run pytest`;
- `uv run ruff check .`;
- `uv run mypy src`;
- `docker compose config`;
- `bash -n scripts/*.sh`.

The same checks can be run locally:

```bash
cd 01-ai-marketing-ops-agent
./scripts/run_ci_locally.sh
```

## How to Run Locally

Prerequisites:

- Python 3.12+
- `uv`
- Docker and Docker Compose

Setup:

```bash
cd 01-ai-marketing-ops-agent
uv sync
uv run playwright install chromium
```

Start mock services:

```bash
./scripts/start_services.sh
```

Run the deterministic workflow:

```bash
./scripts/run_workflow.sh
```

Run with deterministic mock LLM interpretation:

```bash
./scripts/run_workflow_with_llm.sh
```

Run with deterministic mock notification delivery:

```bash
NOTIFICATION_DELIVERY_ENABLED=true ./scripts/run_workflow.sh
```

Inspect outputs:

```bash
ls -lt reports/
sed -n '1,220p' "$(ls -t reports/*.md | head -n 1)"
tail -n 5 run-history/workflow-runs.jsonl
tail -n 20 approval-requests/approval-requests.jsonl
```

Clean generated runtime files:

```bash
./scripts/clean_runtime.sh
```

## What This Demonstrates

Project 1 demonstrates practical AI automation engineering:

- choosing API integration versus browser automation;
- typed service boundaries with validation and timeouts;
- deterministic data aggregation before LLM interpretation;
- explicit data quality handling;
- deterministic anomaly detection;
- report generation suitable for stakeholder review;
- workflow orchestration with dependency injection;
- local audit trails through run history and approval queues;
- human approval gates for high-risk actions;
- optional LLM interpretation that is downstream and controlled;
- approval-aware notification behavior without real external providers;
- CI/CD checks that reviewers can see and reproduce locally.

## Limitations / Next Steps

Project 1 intentionally stays local and demo-safe:

- real Slack, Telegram and email providers are not implemented;
- no production database is used;
- mock services stand in for real marketing systems;
- approval decisions are stored locally instead of in a shared approval UI;
- Docker image publishing and deployment are not included.

The handoff points to Project 2 next: MCP Automation Server + Claude Code
Toolkit.
