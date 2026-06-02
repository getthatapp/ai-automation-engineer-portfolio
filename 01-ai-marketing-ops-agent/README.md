# AI Marketing Operations Agent

Production-oriented portfolio project for automating a daily marketing operations workflow.

The goal is not to build a chatbot. The goal is to demonstrate a controlled, testable and observable AI automation workflow that combines deterministic automation, API integrations, browser automation where needed, retries, fallbacks, validation, human approval and selective LLM interpretation.

## Current status

Milestones 1-13 are completed.

Completed scope:

- Python 3.12+ project managed with `uv`.
- Pydantic v2 domain models.
- Retry and async rate limiter utilities.
- Local FastAPI mock services for the marketing panel, Campaign REST API, Analytics GraphQL API and project management API.
- Typed `httpx` clients for the REST and GraphQL mock services.
- Async Playwright scraper for the HTML-only marketing panel.
- Deterministic aggregation layer that joins scraped panel rows, Campaign REST API metadata and Analytics GraphQL metrics.
- Validated `CampaignSnapshot` business object for downstream modules.
- Deterministic anomaly detection over `CampaignSnapshot` objects, including performance rules and data quality escalation.
- Deterministic Markdown report writer over `CampaignSnapshot` and `AnomalyFinding` objects.
- Deterministic daily report workflow orchestration that scrapes, aggregates, detects anomalies, writes a Markdown report to `reports/` and can optionally create project management tasks for critical or human-review findings.
- Persistent local run recording to JSONL under `run-history/`, including success/failure status, timings, output paths, counts, task IDs, data quality summaries and sanitized failure messages.
- Optional LLM interpretation layer over validated `CampaignSnapshot`, `AnomalyFinding`, deterministic report summary and optional run record inputs.
- Deterministic mock LLM provider for tests and local no-key runs, with token usage capture when a provider returns it.
- Deterministic human approval flow with local JSONL approval queue for critical findings, human-review findings and high-risk LLM recommendations.
- Optional approval-aware notification delivery over completed workflow summaries.
- Deterministic mock notification provider for tests and local no-key demos.
- GitHub Actions CI for tests, linting, typing, Compose validation and script syntax checks.
- Minimal pytest coverage and project documentation placeholders.
- Claude/Codex-ready marketing report skill.

Real Slack, Telegram and email providers are intentionally left for later
milestones. The current provider is local, deterministic and does not call
external notification APIs.

## Requirements

- Python 3.12+
- `uv`
- Docker and Docker Compose for the local mock environment

## Setup

```bash
uv sync
cp .env.example .env
uv run playwright install chromium
```

Fill `.env` only with local values. Do not commit secrets.

## Local reviewer demo flow

This flow is intended for external reviewers and recruiters who want to run the
project without relying on personal shell aliases.

Prerequisites:

- Python 3.12+
- `uv`
- Docker and Docker Compose

Install dependencies and Playwright's Chromium runtime:

```bash
uv sync
uv run playwright install chromium
```

Start the local mock services:

```bash
./scripts/start_services.sh
```

Run the deterministic workflow:

```bash
./scripts/run_workflow.sh
```

Run the workflow with the deterministic mock LLM interpretation layer:

```bash
./scripts/run_workflow_with_llm.sh
```

Run the workflow with deterministic mock notification delivery:

```bash
NOTIFICATION_DELIVERY_ENABLED=true ./scripts/run_workflow.sh
```

The workflow scripts set safe local defaults for the mock marketing panel:

```text
MARKETING_PANEL_USERNAME=demo@example.com
MARKETING_PANEL_PASSWORD=local-password
MARKETING_PANEL_2FA_CODE=000000
```

They also default to the local mock service URLs. Any of these values can be
overridden with environment variables before invoking the script. No real
secrets, external LLM key or real notification credentials are required when
`LLM_PROVIDER=mock` and `NOTIFICATION_PROVIDER=mock`.

Inspect the latest report:

```bash
ls -lt reports/
sed -n '1,220p' "$(ls -t reports/*.md | head -n 1)"
```

Inspect recent workflow run history:

```bash
tail -n 5 run-history/workflow-runs.jsonl
```

Inspect approval requests when present:

```bash
tail -n 20 approval-requests/approval-requests.jsonl
```

Run quality checks:

```bash
./scripts/run_checks.sh
```

Run the full local CI mirror:

```bash
./scripts/run_ci_locally.sh
```

Clean generated runtime files:

```bash
./scripts/clean_runtime.sh
```

Stop the mock services:

```bash
docker compose down
```

Generated reports, run history and approval request files are ignored by git.

## Local mock environment

Run all mock services:

```bash
docker compose up --build
```

Or use the reviewer helper script:

```bash
./scripts/start_services.sh
```

Services:

- Marketing panel without API: `http://localhost:8000`
- Campaign REST API: `http://localhost:8001`
- Analytics GraphQL API: `http://localhost:8002/graphql`
- Project management REST API: `http://localhost:8003`

Mock marketing panel credentials:

- Username: `demo@example.com`
- Password: `local-password`
- Mock 2FA code: `000000`

Run services directly without Docker:

```bash
uv run uvicorn marketing_ops_agent.mock_services.marketing_panel:app --reload --port 8000
uv run uvicorn marketing_ops_agent.mock_services.campaign_api:app --reload --port 8001
uv run uvicorn marketing_ops_agent.mock_services.analytics_graphql_api:app --reload --port 8002
uv run uvicorn marketing_ops_agent.mock_services.project_management_api:app --reload --port 8003
```

## Marketing panel scraper

The marketing panel is scraped with Playwright because it deliberately does not expose an API. The scraper targets only the local mock panel and uses a deterministic mock 2FA field. It does not contain real CAPTCHA bypass logic.

Run only the mock panel:

```bash
docker compose up --build marketing-panel
```

Manual scraper run:

```bash
MARKETING_PANEL_USERNAME=demo@example.com \
MARKETING_PANEL_PASSWORD=local-password \
MARKETING_PANEL_2FA_CODE=000000 \
uv run python -c 'import asyncio; from marketing_ops_agent.browser import PlaywrightMarketingPanelScraper; rows = asyncio.run(PlaywrightMarketingPanelScraper().scrape_campaign_rows()); print([row.model_dump() for row in rows])'
```

## Deterministic aggregation layer

The aggregation layer lives in `marketing_ops_agent.aggregation`. It accepts scraped marketing panel rows, fetches related Campaign REST API metadata and Analytics GraphQL metrics, then produces validated `CampaignSnapshot` objects.

The layer is deterministic:

- it does not call an LLM;
- it does not invent missing metrics;
- it does not silently drop rows with missing or inconsistent service data;
- it preserves source records for auditability;
- it marks quality issues explicitly for review and downstream handling.

Each `CampaignSnapshot` contains:

- `campaign_id`
- `scraped_row`
- `campaign_metadata`
- `analytics_metrics`
- `data_quality_flags`
- `data_quality_notes`
- `requires_human_review`
- `aggregated_at`

`CampaignSnapshot` is now the validated business object for downstream modules. Anomaly detection, recommendation generation, report writing, approvals and task creation should consume `CampaignSnapshot`, not raw scraped rows, raw REST payloads or raw GraphQL responses.

## Data quality flags

The aggregation layer can attach these data quality flags:

- `missing_campaign_metadata`
- `missing_analytics_metrics`
- `spend_mismatch`
- `conversions_mismatch`
- `revenue_mismatch`
- `stale_data`
- `requires_human_review`

These flags make data quality problems explicit before automated action is considered. Any snapshot with `requires_human_review` should be blocked from sensitive automated follow-up until reviewed.

## Deterministic anomaly detection

The anomaly layer lives in `marketing_ops_agent.anomaly`. It consumes validated
`CampaignSnapshot` objects and returns typed `AnomalyFinding` models without
calling external services or an LLM.

Implemented deterministic checks:

- high spend with low conversions;
- CPA above a configurable threshold;
- ROI below a configurable threshold;
- data quality flag mapping for missing metadata, missing analytics metrics, source mismatches, stale data and human review escalation.

Default thresholds:

- `max_cpa`: `50.0`
- `min_roi`: `0.0`
- `high_spend_threshold`: `10000.0`
- `low_conversion_threshold`: `10`

Minimal usage:

```python
from marketing_ops_agent.anomaly import AnomalyDetector, AnomalyThresholds

detector = AnomalyDetector(
    thresholds=AnomalyThresholds(max_cpa=75.0, min_roi=0.0)
)
findings = detector.detect(snapshots)
```

The detector calculates CPA and ROI from available panel metrics and preserves
source evidence from each available snapshot source. It does not invent missing
Campaign API or Analytics GraphQL values.

## Deterministic Markdown reporting

The reporting layer lives in `marketing_ops_agent.reporting`. It consumes
validated `CampaignSnapshot` objects and typed `AnomalyFinding` objects, then
returns a Markdown string. It does not consume raw scraped rows, raw REST
responses or raw GraphQL responses.

Implemented report sections:

- report title and generated timestamp;
- executive summary;
- campaign health overview;
- critical anomalies;
- warning anomalies;
- data quality issues;
- human review required;
- campaign snapshot table;
- deterministic recommended actions;
- limitations / missing data.

Minimal usage:

```python
from datetime import UTC, datetime

from marketing_ops_agent.reporting import ReportMetadata, generate_markdown_report


metadata = ReportMetadata(
    title="Daily Marketing Operations Report",
    generated_at=datetime.now(UTC),
)
report_markdown = generate_markdown_report(snapshots, findings, metadata)
```

Findings are sorted deterministically by severity, campaign ID, anomaly type,
message and source. Campaigns are sorted by `campaign_id`. Missing Campaign API
or Analytics GraphQL values are shown as `missing` and are not inferred.

## Daily marketing report workflow

The workflow layer lives in `marketing_ops_agent.workflows`. It connects the
existing deterministic components:

1. scrape local marketing panel rows with Playwright;
2. fetch Campaign REST API metadata and Analytics GraphQL metrics through typed clients;
3. aggregate validated `CampaignSnapshot` objects;
4. detect deterministic `AnomalyFinding` objects;
5. render a deterministic Markdown report;
6. save the report under `reports/`;
7. optionally run LLM interpretation;
8. create local human approval requests for high-risk outputs;
9. optionally create deterministic project management tasks;
10. optionally send an approval-aware notification summary.

Manual local run after starting mock services:

```bash
./scripts/run_workflow.sh
```

The manual equivalent is:

```bash
MARKETING_PANEL_USERNAME=demo@example.com \
MARKETING_PANEL_PASSWORD=local-password \
MARKETING_PANEL_2FA_CODE=000000 \
uv run python -m marketing_ops_agent.workflows.daily_marketing_report
```

Programmatic usage:

```python
import asyncio

from marketing_ops_agent.workflows import run_daily_marketing_report_workflow


result = asyncio.run(
    run_daily_marketing_report_workflow(
        reports_dir="reports",
        create_project_tasks=False,
    )
)
print(result.status, result.report_path)
```

Generated Markdown reports are ignored by git. Only `reports/.gitkeep` is kept
so the local output directory exists in a fresh checkout.

Optional task creation is deterministic and limited to findings that are
critical or require human review. Duplicate task requests for the same campaign
and anomaly type are suppressed within one workflow run.

## Approval-aware notifications

The notification layer lives in `marketing_ops_agent.notifications`. It sends
summary-only notifications after workflow completion when enabled. The summary
includes:

- run ID and report path;
- snapshot, finding and critical finding counts;
- whether human review is required;
- pending approval request IDs when approval requests exist.

Pending approval requests are explicitly described as not approved actions. The
notification payload does not include raw scraped rows, raw REST responses, raw
GraphQL responses, credentials, secrets or sensitive recommendations as approved
work.

Local notification delivery is disabled by default. Enable the deterministic
mock provider for a local demo:

```bash
NOTIFICATION_DELIVERY_ENABLED=true \
NOTIFICATION_PROVIDER=mock \
./scripts/run_workflow.sh
```

Programmatic usage:

```python
import asyncio

from marketing_ops_agent.notifications import NotificationService


service = NotificationService()
result = asyncio.run(
    service.send_report_summary(
        run_id="daily-marketing-report-20260528T120000Z",
        report_path="reports/daily-marketing-report-20260528T120000Z.md",
        snapshot_count=3,
        finding_count=2,
        critical_finding_count=1,
        human_review_required=True,
        pending_approval_request_ids=("approval-001",),
    )
)
print(result.status, result.notification_id)
```

The workflow records notification status and count in local run history when a
notification service is configured. Delivery failures are logged and returned
as `NotificationResult(status="failed")` without failing report generation.

## Human approval flow

The approval layer lives in `marketing_ops_agent.approval`. It creates pending
approval requests for:

- critical deterministic findings;
- deterministic findings with `requires_human_review=True`;
- high-priority or human-approval LLM recommended actions.

Approval requests are deterministic, deduplicated within one workflow run and
never auto-approved. They preserve run ID, campaign ID, source type, risk level,
source reference and sanitized source evidence.

Local persistence defaults to:

```text
approval-requests/approval-requests.jsonl
```

Manual inspection:

```bash
tail -n 20 approval-requests/approval-requests.jsonl
```

Programmatic usage:

```python
from marketing_ops_agent.approval import LocalApprovalStore


store = LocalApprovalStore("approval-requests/approval-requests.jsonl")
pending = store.list_pending()
approved = store.approve(
    pending[0].approval_id,
    decided_by="manager@example.com",
    reason="Evidence reviewed.",
)
```

Generated approval files are ignored by git. Only
`approval-requests/.gitkeep` is checked in.

## Persistent run recording

The observability layer lives in `marketing_ops_agent.observability`. The local
runner records workflow summaries to JSONL by default:

```text
run-history/workflow-runs.jsonl
```

Each `WorkflowRunRecord` captures:

- run identity, workflow name, status and UTC timestamps;
- duration in seconds;
- report path when a report was saved;
- snapshot, finding, critical finding and task error counts;
- human-review requirement;
- approval request count;
- notification status and count when notification delivery is configured;
- created project task IDs;
- data quality flag counts;
- sanitized failure type and message for unrecoverable workflow failures.

Manual inspection:

```bash
tail -n 5 run-history/workflow-runs.jsonl
```

Programmatic inspection:

```python
from marketing_ops_agent.observability import LocalRunRecorder


recorder = LocalRunRecorder("run-history/workflow-runs.jsonl")
recent_runs = recorder.read_recent(limit=10)
specific_run = recorder.get("daily-marketing-report-20260528T120000Z")
```

Generated JSONL run history is ignored by git. Only `run-history/.gitkeep` is
checked in so the local directory exists in a fresh checkout.

## Typed client usage

The clients read safe local defaults from environment variables:

- `CAMPAIGN_API_BASE_URL`
- `ANALYTICS_GRAPHQL_URL`
- `PROJECT_MANAGEMENT_API_BASE_URL`
- `REQUEST_TIMEOUT_SECONDS`
- `RETRY_MAX_ATTEMPTS`

Example:

```python
import asyncio

from marketing_ops_agent.clients import (
    AnalyticsClient,
    CampaignClient,
    ProjectManagementClient,
    ProjectTaskCreate,
)


async def main() -> None:
    async with CampaignClient() as campaign_client:
        campaign = await campaign_client.get_campaign("cmp-search-brand")

    async with AnalyticsClient() as analytics_client:
        metrics = await analytics_client.get_campaign_metrics(campaign.campaign_id)

    async with ProjectManagementClient() as task_client:
        await task_client.create_task(
            ProjectTaskCreate(
                title=f"Review {campaign.name}",
                description=f"Current campaign cost is {metrics.cost}.",
                campaign_id=campaign.campaign_id,
            )
        )


asyncio.run(main())
```

## Optional LLM interpretation

The LLM layer lives in `marketing_ops_agent.llm`. It consumes only validated
deterministic outputs:

- `CampaignSnapshot` objects;
- `AnomalyFinding` objects;
- deterministic Markdown report text or a summary;
- optional `WorkflowRunRecord`.

It does not read raw scraped rows, raw REST responses, raw GraphQL responses,
credentials or environment variables. Prompt construction includes explicit
rules to avoid invented metrics, preserve data quality flags, keep facts
separate from recommendations and respect human-review gates.

By default, tests and local no-key runs use `DeterministicMockLLMProvider`.
No external LLM API is called by the test suite.

Minimal usage:

```python
from marketing_ops_agent.llm import LLMInterpretationRequest, LLMInterpreter


interpreter = LLMInterpreter()
result = await interpreter.interpret(
    LLMInterpretationRequest(
        snapshots=tuple(snapshots),
        findings=tuple(findings),
        deterministic_report_summary=report_markdown,
    )
)
print(result.status, result.summary, result.token_usage)
```

The daily workflow remains deterministic by default. To enable the optional
interpretation hook in the local runner:

```python
result = asyncio.run(
    run_daily_marketing_report_workflow(enable_llm_interpretation=True)
)
print(result.llm_interpretation)
```

Equivalent environment configuration:

```text
LLM_INTERPRETATION_ENABLED=true
LLM_PROVIDER=mock
LLM_MODEL=deterministic-marketing-interpreter
```

Reviewer helper:

```bash
./scripts/run_workflow_with_llm.sh
```

## Optional notification configuration

```text
NOTIFICATION_DELIVERY_ENABLED=true
NOTIFICATION_PROVIDER=mock
```

Only the deterministic mock provider is implemented. Real Slack, Telegram or
email credentials should remain empty until real providers are added.

## Tests and quality checks

Run tests:

```bash
./scripts/run_checks.sh
```

Equivalent individual commands:

```bash
uv run pytest
uv run ruff check .
uv run mypy src
```

## CI/CD

Project 1 includes a GitHub Actions workflow at:

```text
.github/workflows/project-1-ci.yml
```

The workflow runs on pull requests and pushes to `main` when Project 1,
repository handoff docs, root instructions, root README or the workflow file
change. It runs from `01-ai-marketing-ops-agent` and validates:

- `uv sync`;
- `uv run playwright install chromium`;
- `uv run pytest`;
- `uv run ruff check .`;
- `uv run mypy src`;
- `docker compose config`;
- `bash -n scripts/*.sh`.

CI does not start long-lived Docker Compose services, call real external APIs,
send real notifications or require secrets. LLM interpretation and notification
delivery are disabled by default, and the implemented providers are deterministic
mocks.

Run the same check set locally:

```bash
./scripts/run_ci_locally.sh
```

## Next milestone

The next milestone should start Project 2: MCP Automation Server + Claude Code Toolkit.
