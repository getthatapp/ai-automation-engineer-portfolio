# Architecture

## Workflow Boundaries

Project 1 models a daily marketing operations workflow. The workflow collects
campaign data from three deterministic local sources:

- Marketing panel rows scraped with Playwright because the panel has no API.
- Campaign metadata from the Campaign REST API.
- Campaign metrics from the Analytics GraphQL API.

The LLM workflow is intentionally not implemented yet. Current logic stops at
deterministic collection, aggregation, validation, anomaly detection and
Markdown report generation orchestrated by the daily workflow.

## API-First Strategy

The Campaign REST API and Analytics GraphQL API are accessed through typed
`httpx` clients with timeout, retry and response validation. Playwright is only
used for the mock marketing panel because that surface deliberately exposes no
API.

## Aggregation Layer

`marketing_ops_agent.aggregation.CampaignAggregator` joins source data by
`campaign_id` and returns one `CampaignSnapshot` per scraped panel row.

Each snapshot preserves source data separately:

- `scraped_row`
- `campaign_metadata`
- `analytics_metrics`

This avoids choosing a silent source of truth when systems disagree. The
snapshot also includes `data_quality_flags`, `data_quality_notes`,
`requires_human_review` and `aggregated_at`.

## Data Quality

The aggregation layer currently marks:

- `missing_campaign_metadata`
- `missing_analytics_metrics`
- `spend_mismatch`
- `conversions_mismatch`
- `revenue_mismatch`
- `stale_data`
- `requires_human_review`

Missing data and critical mismatches require human review. The aggregator does
not invent missing values and does not drop mismatched rows.

## Anomaly Detection Layer

`marketing_ops_agent.anomaly.AnomalyDetector` consumes `CampaignSnapshot`
objects and returns typed `AnomalyFinding` objects. The detector is synchronous
because it analyzes already collected in-memory data.

The detector has two responsibilities:

- evaluate explicit performance rules from available panel metrics;
- map aggregation `DataQualityFlag` values into anomaly findings.

Performance rules currently cover:

- high spend with low conversions;
- CPA above the configured maximum;
- ROI below the configured minimum.

CPA is calculated as `spend / conversions` only when conversions are greater
than zero. ROI is calculated as `(revenue - spend) / spend` only when spend is
greater than zero. Missing Campaign API or Analytics GraphQL values are not
invented. Findings include source evidence from the panel and from each
available API source.

The default thresholds are held in `AnomalyThresholds` and can be overridden at
detector construction time.

## Reporting Layer

`marketing_ops_agent.reporting.MarkdownReportWriter` consumes only
`CampaignSnapshot` and `AnomalyFinding` objects. It returns a deterministic
Markdown string and does not call external services or an LLM.

The writer renders these sections:

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

Campaign rows are sorted by `campaign_id`. Findings are sorted by severity
first, then campaign ID, anomaly type, message and source. Missing Campaign API
or Analytics GraphQL values are shown as `missing`; the writer does not infer
unavailable metrics or recalculate anomaly rules.

## Workflow Orchestration Layer

`marketing_ops_agent.workflows.DailyMarketingReportWorkflow` is the executable
deterministic pipeline for Milestone 8. It coordinates existing components
without introducing LLM calls or external notification integrations.

Workflow order:

1. scrape campaign rows from the local marketing panel;
2. aggregate Campaign REST API metadata and Analytics GraphQL metrics into
   `CampaignSnapshot` objects;
3. pass snapshots into anomaly detection;
4. pass findings into the Markdown report writer;
5. save the report under a local reports directory;
6. optionally create project management tasks.

The workflow uses dependency injection for the scraper, clients, detector,
report writer and optional task client. Tests can replace every boundary with
fakes while production-local runs use `PlaywrightMarketingPanelScraper`,
`CampaignClient`, `AnalyticsClient`, `AnomalyDetector` and
`MarkdownReportWriter`.

The typed result is `DailyMarketingReportResult`. It records the run ID,
status, timestamps, report path, row/snapshot/finding counts, snapshots,
findings, created tasks and non-fatal task creation errors.

Report paths are deterministic from the run timestamp:

```text
reports/daily-marketing-report-YYYYMMDDTHHMMSSZ.md
```

Generated reports are local artifacts and are ignored by git except for
`reports/.gitkeep`.

## Project Task Rules

Task creation is optional. When a task client is provided, the workflow creates
tasks only for findings with `severity=critical` or
`requires_human_review=True`.

Task request text is deterministic:

- title: `Review {anomaly_type} for {campaign_id}`;
- description: campaign ID, anomaly type, severity, human-review flag, source,
  finding message and sorted source evidence.

Duplicate task requests for the same `(campaign_id, anomaly_type)` are
suppressed within one run. Service-level task creation failures do not block
report generation; they are recorded in `task_creation_errors`.

## LLM Boundary

Future LLM usage is limited to interpretation, summarization and
recommendations after deterministic validation and anomaly detection have
produced campaign snapshots, typed findings and a deterministic report
baseline. LLM prompts must consume the explicit data quality flags and anomaly
findings rather than infer source reliability.

## Human Approval

`CampaignSnapshot.requires_human_review` is the first checkpoint for later
approval flow. `AnomalyFinding.requires_human_review` is the second checkpoint
for rule-level escalations. The workflow already uses finding-level human
review requirements when deciding whether to create deterministic project
management tasks. Later milestones should add explicit approval state before
sending reports or recommending sensitive campaign changes.
