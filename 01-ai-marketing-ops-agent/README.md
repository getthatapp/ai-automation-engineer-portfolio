# AI Marketing Operations Agent

Production-oriented portfolio project for automating a daily marketing operations workflow.

The goal is not to build a chatbot. The goal is to demonstrate a controlled, testable and observable AI automation workflow that combines deterministic automation, API integrations, browser automation where needed, retries, fallbacks, validation, human approval and selective LLM interpretation.

## Current status

Milestones 1-8 are completed.

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
- Minimal pytest coverage and project documentation placeholders.
- Claude/Codex-ready marketing report skill.

The full LLM report workflow, persistent run recording and external notification delivery are intentionally left for later milestones.

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

## Local mock environment

Run all mock services:

```bash
docker compose up --build
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
7. optionally create deterministic project management tasks.

Manual local run after starting mock services:

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

## Tests and quality checks

Run tests:

```bash
uv run pytest
```

Run linting and type checks:

```bash
uv run ruff check .
uv run mypy src
```

## Next milestone

The next milestone should add persistent run recording and observability around
workflow status, failures and retry counts. LLM-based interpretation should
still remain downstream of deterministic validation, anomaly detection and
report generation.
