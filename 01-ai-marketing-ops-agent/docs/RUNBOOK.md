# Runbook

## Environment Setup

```bash
uv sync
cp .env.example .env
uv run playwright install chromium
```

Do not commit `.env`. The checked-in `.env.example` contains only local mock
defaults and empty placeholders for optional integrations.

## Reviewer Demo Flow

The `scripts/` directory contains local wrappers for reviewers who do not have
project-specific shell aliases.

Start the local mock services:

```bash
./scripts/start_services.sh
```

Run the deterministic workflow:

```bash
./scripts/run_workflow.sh
```

Run the workflow with deterministic mock LLM interpretation:

```bash
./scripts/run_workflow_with_llm.sh
```

Both workflow scripts use local mock marketing panel credentials by default:

| Environment variable | Default |
| --- | --- |
| `MARKETING_PANEL_USERNAME` | `demo@example.com` |
| `MARKETING_PANEL_PASSWORD` | `local-password` |
| `MARKETING_PANEL_2FA_CODE` | `000000` |

Environment variables can override script defaults. Do not use real secrets for
the local mock demo.

Inspect generated outputs:

```bash
ls -lt reports/
sed -n '1,220p' "$(ls -t reports/*.md | head -n 1)"
tail -n 5 run-history/workflow-runs.jsonl
tail -n 20 approval-requests/approval-requests.jsonl
```

Run quality checks:

```bash
./scripts/run_checks.sh
```

Clean generated runtime files:

```bash
./scripts/clean_runtime.sh
```

Generated reports, run history and approval request records are ignored by git.

## Mock Service Startup

Run all local mock services with Docker Compose:

```bash
docker compose up --build
```

Detached helper:

```bash
./scripts/start_services.sh
```

The Compose stack starts four independent FastAPI services:

| Service | URL | Purpose |
| --- | --- | --- |
| Marketing panel | `http://localhost:8000` | HTML-only panel for later Playwright automation |
| Campaign REST API | `http://localhost:8001` | Campaign list and detail endpoints |
| Analytics GraphQL API | `http://localhost:8002/graphql` | Campaign metrics query endpoint |
| Project management API | `http://localhost:8003` | Mock task creation and listing |

Stop services:

```bash
docker compose down
```

## Mock Marketing Panel

Endpoints:

- `GET /login`
- `POST /login`
- `GET /dashboard`

Credentials:

- Username: `demo@example.com`
- Password: `local-password`
- Mock 2FA code: `000000`

The 2FA field is deliberately deterministic for local testing. There is no real
CAPTCHA and no CAPTCHA bypass logic.

## Marketing Panel Scraper

The scraper lives in `marketing_ops_agent.browser` and uses Playwright's async
API against the local mock marketing panel only.

Install the browser runtime once:

```bash
uv run playwright install chromium
```

Start the marketing panel:

```bash
docker compose up --build marketing-panel
```

Required environment variables:

| Environment variable | Local mock value |
| --- | --- |
| `MARKETING_PANEL_BASE_URL` | `http://localhost:8000` |
| `MARKETING_PANEL_USERNAME` | `demo@example.com` |
| `MARKETING_PANEL_PASSWORD` | `local-password` |
| `MARKETING_PANEL_2FA_CODE` | `000000` |

Manual run:

```bash
MARKETING_PANEL_USERNAME=demo@example.com \
MARKETING_PANEL_PASSWORD=local-password \
MARKETING_PANEL_2FA_CODE=000000 \
uv run python -c 'import asyncio; from marketing_ops_agent.browser import PlaywrightMarketingPanelScraper; rows = asyncio.run(PlaywrightMarketingPanelScraper().scrape_campaign_rows()); print([row.model_dump() for row in rows])'
```

Custom scraper errors:

- `MarketingPanelLoginFailedError`
- `DashboardUnavailableError`
- `CampaignTableNotFoundError`
- `MalformedCampaignRowError`

## Campaign REST API

Endpoints:

- `GET /api/campaigns`
- `GET /api/campaigns/{campaign_id}`

Example:

```bash
curl http://localhost:8001/api/campaigns
```

## Analytics GraphQL API

Endpoint:

- `POST /graphql`

Example:

```bash
curl -X POST http://localhost:8002/graphql \
  -H 'content-type: application/json' \
  -d '{
    "query": "query CampaignMetrics($campaignId: String!) { campaignMetrics(campaignId: $campaignId) { impressions clicks conversions revenue cost } }",
    "variables": {"campaignId": "cmp-search-brand"}
  }'
```

The mock supports:

- `campaignMetrics(campaignId: ...)`
- `allCampaignMetrics`

## Project Management API

Endpoints:

- `POST /api/tasks`
- `GET /api/tasks`

Example:

```bash
curl -X POST http://localhost:8003/api/tasks \
  -H 'content-type: application/json' \
  -d '{
    "title": "Review high-spend search campaign",
    "description": "Check ROAS movement before changing budget.",
    "campaign_id": "cmp-search-brand"
  }'
```

## Verification

```bash
./scripts/run_checks.sh
```

Equivalent individual commands are `uv run pytest`, `uv run ruff check .` and
`uv run mypy src`.

## Typed Client Usage

The typed service clients live in `marketing_ops_agent.clients`.

Configuration defaults:

| Environment variable | Default |
| --- | --- |
| `CAMPAIGN_API_BASE_URL` | `http://localhost:8001` |
| `ANALYTICS_GRAPHQL_URL` | `http://localhost:8002/graphql` |
| `PROJECT_MANAGEMENT_API_BASE_URL` | `http://localhost:8003` |
| `REQUEST_TIMEOUT_SECONDS` | `15` |
| `RETRY_MAX_ATTEMPTS` | `3` |

Example:

```python
from marketing_ops_agent.clients import AnalyticsClient, CampaignClient


async def collect_campaign_snapshot(campaign_id: str) -> None:
    async with CampaignClient() as campaign_client:
        campaign = await campaign_client.get_campaign(campaign_id)

    async with AnalyticsClient() as analytics_client:
        metrics = await analytics_client.get_campaign_metrics(campaign.campaign_id)

    print(campaign.name, metrics.revenue)
```

Client error handling:

- HTTP 4xx responses raise `ServiceResponseError`.
- HTTP 5xx responses raise `RetryableServiceResponseError` and are retried.
- Timeouts raise `ServiceTimeoutError` and are retried.
- Transport failures raise `ServiceConnectionError` and are retried.
- Invalid response shapes raise `ServiceDecodeError`.
- GraphQL `errors` responses raise `GraphQLResponseError`.

## Campaign Aggregation

The deterministic aggregation layer lives in `marketing_ops_agent.aggregation`.
It accepts rows from the Playwright scraper, fetches Campaign REST API metadata
and Analytics GraphQL metrics, then returns `CampaignSnapshot` models.

Minimal local usage:

```python
from marketing_ops_agent.aggregation import CampaignAggregator
from marketing_ops_agent.browser import PlaywrightMarketingPanelScraper
from marketing_ops_agent.clients import AnalyticsClient, CampaignClient


async def collect_snapshots() -> None:
    async with PlaywrightMarketingPanelScraper() as scraper:
        rows = await scraper.scrape_campaign_rows()

    async with CampaignClient() as campaign_client:
        async with AnalyticsClient() as analytics_client:
            aggregator = CampaignAggregator(
                campaign_client=campaign_client,
                analytics_client=analytics_client,
            )
            snapshots = await aggregator.aggregate(rows)

    for snapshot in snapshots:
        print(snapshot.campaign_id, snapshot.data_quality_flags)
```

Data quality flags:

- `missing_campaign_metadata`
- `missing_analytics_metrics`
- `spend_mismatch`
- `conversions_mismatch`
- `revenue_mismatch`
- `stale_data`
- `requires_human_review`

Rows with missing or mismatched source data are not dropped. Check
`requires_human_review` before taking automated follow-up action.

## Anomaly Detection

The deterministic anomaly layer lives in `marketing_ops_agent.anomaly`. It
requires no running service because it analyzes in-memory `CampaignSnapshot`
objects.

Minimal usage:

```python
from marketing_ops_agent.anomaly import AnomalyDetector, AnomalyThresholds


detector = AnomalyDetector(
    thresholds=AnomalyThresholds(
        max_cpa=50.0,
        min_roi=0.0,
        high_spend_threshold=10_000.0,
        low_conversion_threshold=10,
    )
)
findings = detector.detect(snapshots)

for finding in findings:
    print(finding.campaign_id, finding.anomaly_type, finding.severity)
```

Implemented anomaly types:

- `high_spend_low_conversions`
- `cpa_above_threshold`
- `negative_roi`
- `missing_campaign_metadata`
- `missing_analytics_metrics`
- `spend_mismatch`
- `conversions_mismatch`
- `revenue_mismatch`
- `stale_data`
- `requires_human_review`

Critical findings and findings with `requires_human_review=True` should block
automated follow-up until a human has reviewed the campaign evidence.

## Markdown Report Generation

The deterministic report writer lives in `marketing_ops_agent.reporting`. It
requires no running service because it renders already collected
`CampaignSnapshot` objects and `AnomalyFinding` objects.

Minimal usage:

```python
from datetime import UTC, datetime

from marketing_ops_agent.reporting import ReportMetadata, generate_markdown_report


metadata = ReportMetadata(
    title="Daily Marketing Operations Report",
    generated_at=datetime.now(UTC),
)
report_markdown = generate_markdown_report(snapshots, findings, metadata)
print(report_markdown)
```

The report includes:

- executive summary;
- campaign health overview;
- critical and warning anomalies;
- data quality issues;
- human review required;
- campaign snapshot table;
- deterministic recommended actions;
- limitations and missing data.

Operational notes:

- Campaigns are sorted by `campaign_id`.
- Findings are sorted critical first, then warning, then info.
- Missing Campaign API or Analytics GraphQL values are rendered as `missing`.
- The writer does not call an LLM, external APIs or notification services.

## Daily Workflow Execution

The deterministic daily workflow lives in `marketing_ops_agent.workflows`. It
scrapes the local marketing panel, fetches Campaign REST API metadata and
Analytics GraphQL metrics, aggregates snapshots, detects anomalies, writes the
Markdown report and saves it locally.

Start all mock services:

```bash
docker compose up --build
```

Run the workflow:

```bash
MARKETING_PANEL_USERNAME=demo@example.com \
MARKETING_PANEL_PASSWORD=local-password \
MARKETING_PANEL_2FA_CODE=000000 \
uv run python -m marketing_ops_agent.workflows.daily_marketing_report
```

The command prints the report path on success.
It also appends a local run record to `run-history/workflow-runs.jsonl`.

Programmatic usage:

```python
import asyncio

from marketing_ops_agent.workflows import run_daily_marketing_report_workflow


result = asyncio.run(run_daily_marketing_report_workflow())
print(result.status, result.report_path)
```

To create deterministic project management tasks for critical or human-review
findings, pass `create_project_tasks=True`:

```python
result = asyncio.run(
    run_daily_marketing_report_workflow(create_project_tasks=True)
)
```

Task creation requires the mock project management API to be running. Task
creation is optional; report generation does not depend on it.

## Optional LLM Interpretation

The optional LLM layer interprets deterministic outputs after snapshots,
findings and the Markdown report already exist. It must not be used to scrape,
join, validate, detect anomalies or replace deterministic report sections.

Environment variables:

| Environment variable | Default | Purpose |
| --- | --- | --- |
| `LLM_INTERPRETATION_ENABLED` | `false` | Enables the optional workflow hook in the local runner |
| `LLM_PROVIDER` | `mock` | Provider label; only the deterministic mock provider is implemented now |
| `LLM_MODEL` | `deterministic-marketing-interpreter` | Model label for interpretation results |
| `OPENAI_API_KEY` | empty | Reserved for a future real provider; not used by tests |

Programmatic usage:

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

Run the local workflow with the optional hook:

```python
result = asyncio.run(
    run_daily_marketing_report_workflow(enable_llm_interpretation=True)
)
print(result.llm_interpretation)
```

Operational notes:

- Tests use `DeterministicMockLLMProvider` and never call external LLM APIs.
- Prompt input is limited to `CampaignSnapshot`, `AnomalyFinding`,
  deterministic report summary and optional `WorkflowRunRecord`.
- Prompt text includes anti-hallucination rules and common inline secret
  redaction.
- Disabled or failed interpretation should not block deterministic report
  generation.
- Token usage is recorded in `LLMInterpretationResult.token_usage` when a
  provider returns it.

## Human Approval Flow

Approval requests are written locally when deterministic findings or LLM
recommendations require review. The default path is:

```text
approval-requests/approval-requests.jsonl
```

Inspect pending requests manually:

```bash
tail -n 20 approval-requests/approval-requests.jsonl
```

Read and decide requests from Python:

```python
from marketing_ops_agent.approval import LocalApprovalStore


store = LocalApprovalStore("approval-requests/approval-requests.jsonl")
pending = store.list_pending()
request = store.get(pending[0].approval_id)
approved = store.approve(
    pending[0].approval_id,
    decided_by="manager@example.com",
    reason="Evidence reviewed.",
)
```

Approval behavior:

- critical deterministic findings create approval requests;
- findings with `requires_human_review=True` create approval requests;
- high-priority or human-approval LLM recommended actions create approval
  requests;
- high-risk actions are never auto-approved;
- duplicate approval requests are suppressed within one workflow run;
- approval storage errors do not block deterministic report generation.

If an approval JSONL line is malformed, `LocalApprovalStore` raises
`MalformedApprovalRecordLineError` with the path and line number.

## Report Output

Reports are written under:

```text
reports/daily-marketing-report-YYYYMMDDTHHMMSSZ.md
```

Generated report files are ignored by git. Keep only `reports/.gitkeep`
checked in.

## Run History Output

Run history is written under:

```text
run-history/workflow-runs.jsonl
```

The file is append-only JSONL. Each line is one `WorkflowRunRecord` with:

- run ID, workflow name, status and UTC timestamps;
- duration in seconds;
- report path;
- snapshot, finding, critical finding and task error counts;
- human-review requirement;
- approval request count;
- created task IDs;
- data quality flag counts;
- sanitized failure type and message for unrecoverable failures.

Inspect recent runs manually:

```bash
tail -n 5 run-history/workflow-runs.jsonl
```

Read recent runs from Python:

```python
from marketing_ops_agent.observability import LocalRunRecorder


recorder = LocalRunRecorder("run-history/workflow-runs.jsonl")
for record in recorder.read_recent(limit=5):
    print(record.run_id, record.status, record.report_path)
```

Read one run by ID:

```python
record = recorder.get("daily-marketing-report-20260528T120000Z")
```

Generated run history files are ignored by git. Keep only
`run-history/.gitkeep` checked in.

## Workflow Result

`DailyMarketingReportResult` includes:

- `run_id`
- `status`
- `started_at` and `finished_at`
- `report_path`
- scraped row, snapshot and finding counts
- `requires_human_review`
- `snapshots`
- `findings`
- `approval_request_ids`
- `created_tasks`
- `task_creation_errors`

Status is `succeeded` when no snapshot or finding requires human review. Status
is `needs_approval` when any snapshot or finding requires human review. These
states are not workflow failures.

## Failure Handling

Partial Campaign REST API or Analytics GraphQL data does not fail the workflow.
The aggregation layer records data quality flags and the anomaly layer turns
those flags into findings.

Unrecoverable failures raise `WorkflowExecutionError` with a step name:

- `scrape_marketing_panel`
- `aggregate_campaign_data`
- `detect_anomalies`
- `write_markdown_report`
- `save_markdown_report`

Task creation service failures are recorded in `task_creation_errors` and do
not delete or block the local Markdown report.

When a local run recorder is configured, successful workflow runs and
unrecoverable workflow failures are persisted. Failed workflow runs still
re-raise `WorkflowExecutionError`; recording does not hide the original
failure.

If a JSONL history line is malformed, `LocalRunRecorder` raises
`MalformedRunRecordLineError` with the path and line number. Do not silently
delete the line unless you have already captured it for investigation.

## Planned Runbook Sections

- approval-aware notification delivery.
