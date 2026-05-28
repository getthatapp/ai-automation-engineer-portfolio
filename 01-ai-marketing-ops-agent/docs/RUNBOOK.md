# Runbook

## Environment Setup

```bash
uv sync
cp .env.example .env
```

Do not commit `.env`. The checked-in `.env.example` contains only local mock
defaults and empty placeholders for optional integrations.

## Mock Service Startup

Run all local mock services with Docker Compose:

```bash
docker compose up --build
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
uv run pytest
uv run ruff check .
uv run mypy src
```

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

## Report Output

Reports are written under:

```text
reports/daily-marketing-report-YYYYMMDDTHHMMSSZ.md
```

Generated report files are ignored by git. Keep only `reports/.gitkeep`
checked in.

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

## Planned Runbook Sections

- log inspection,
- retry and failure handling,
- human approval flow.
