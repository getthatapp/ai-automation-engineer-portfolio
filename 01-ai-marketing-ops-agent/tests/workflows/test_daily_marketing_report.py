from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path

import pytest

from marketing_ops_agent.aggregation import CampaignSnapshot, DataQualityFlag
from marketing_ops_agent.anomaly import (
    AnomalyDetector,
    AnomalyFinding,
    AnomalySeverity,
    AnomalyType,
)
from marketing_ops_agent.browser.errors import DashboardUnavailableError
from marketing_ops_agent.browser.panel_scraper import ScrapedCampaignRow
from marketing_ops_agent.clients import ProjectTask, ProjectTaskCreate
from marketing_ops_agent.clients.analytics_client import AnalyticsCampaignMetrics
from marketing_ops_agent.clients.errors import ServiceDecodeError, ServiceResponseError
from marketing_ops_agent.models import Campaign, CampaignMetrics, Channel, WorkflowStatus
from marketing_ops_agent.reporting import ReportMetadata
from marketing_ops_agent.workflows import DailyMarketingReportWorkflow, WorkflowExecutionError

REFERENCE_TIME = datetime(2026, 5, 28, 12, 0, tzinfo=UTC)


class FakeScraper:
    def __init__(
        self,
        rows: Sequence[ScrapedCampaignRow],
        error: Exception | None = None,
    ) -> None:
        self._rows = list(rows)
        self._error = error

    async def scrape_campaign_rows(self) -> list[ScrapedCampaignRow]:
        if self._error is not None:
            raise self._error
        return self._rows


class FakeCampaignClient:
    def __init__(self, campaigns: Mapping[str, Campaign]) -> None:
        self._campaigns = campaigns

    async def get_campaign(self, campaign_id: str) -> Campaign:
        campaign = self._campaigns.get(campaign_id)
        if campaign is None:
            raise ServiceResponseError(status_code=404, response_text="Campaign not found")
        return campaign


class FakeAnalyticsClient:
    def __init__(self, metrics: Mapping[str, AnalyticsCampaignMetrics]) -> None:
        self._metrics = metrics

    async def get_campaign_metrics(self, campaign_id: str) -> AnalyticsCampaignMetrics:
        metrics = self._metrics.get(campaign_id)
        if metrics is None:
            raise ServiceDecodeError("GraphQL response is missing campaignMetrics")
        return metrics


class RecordingDetector:
    def __init__(self, findings: Sequence[AnomalyFinding]) -> None:
        self._findings = list(findings)
        self.received_snapshots: tuple[CampaignSnapshot, ...] = ()

    def detect(self, snapshots: Sequence[CampaignSnapshot]) -> list[AnomalyFinding]:
        self.received_snapshots = tuple(snapshots)
        return self._findings


class RecordingReportWriter:
    def __init__(self, markdown: str = "# deterministic report\n") -> None:
        self._markdown = markdown
        self.received_snapshots: tuple[CampaignSnapshot, ...] = ()
        self.received_findings: tuple[AnomalyFinding, ...] = ()
        self.received_metadata: ReportMetadata | None = None

    def write(
        self,
        snapshots: Sequence[CampaignSnapshot],
        findings: Sequence[AnomalyFinding],
        metadata: ReportMetadata | None = None,
    ) -> str:
        self.received_snapshots = tuple(snapshots)
        self.received_findings = tuple(findings)
        self.received_metadata = metadata
        return self._markdown


class FakeTaskClient:
    def __init__(self) -> None:
        self.requests: list[ProjectTaskCreate] = []

    async def create_task(self, task: ProjectTaskCreate) -> ProjectTask:
        self.requests.append(task)
        return ProjectTask(
            task_id=f"task-{len(self.requests):03d}",
            title=task.title,
            description=task.description,
            campaign_id=task.campaign_id,
            status="open",
            created_at=REFERENCE_TIME,
        )


@pytest.mark.asyncio
async def test_happy_path_workflow_creates_report_and_passes_objects_to_dependencies(
    tmp_path: Path,
) -> None:
    row = _row()
    detector = RecordingDetector(findings=[])
    writer = RecordingReportWriter(markdown="# report\nhealthy\n")
    workflow = _workflow(
        rows=[row],
        detector=detector,
        report_writer=writer,
        reports_dir=tmp_path,
    )

    result = await workflow.run()

    assert result.status is WorkflowStatus.SUCCEEDED
    assert result.run_id == "daily-marketing-report-20260528T120000Z"
    assert result.scraped_rows_count == 1
    assert result.snapshot_count == 1
    assert result.finding_count == 0
    assert result.report_path == tmp_path / "daily-marketing-report-20260528T120000Z.md"
    assert result.report_path.read_text(encoding="utf-8") == "# report\nhealthy\n"
    assert detector.received_snapshots == result.snapshots
    assert writer.received_snapshots == result.snapshots
    assert writer.received_findings == result.findings
    assert writer.received_metadata == ReportMetadata(generated_at=REFERENCE_TIME)


@pytest.mark.asyncio
async def test_findings_are_passed_into_report_writer(tmp_path: Path) -> None:
    finding = _finding(
        anomaly_type=AnomalyType.CPA_ABOVE_THRESHOLD,
        severity=AnomalySeverity.WARNING,
        message="Campaign CPA is above threshold.",
    )
    writer = RecordingReportWriter()
    workflow = _workflow(
        rows=[_row()],
        detector=RecordingDetector(findings=[finding]),
        report_writer=writer,
        reports_dir=tmp_path,
    )

    result = await workflow.run()

    assert writer.received_findings == (finding,)
    assert result.findings == (finding,)


@pytest.mark.asyncio
async def test_critical_findings_create_deterministic_deduplicated_tasks(
    tmp_path: Path,
) -> None:
    finding = _finding(
        anomaly_type=AnomalyType.NEGATIVE_ROI,
        severity=AnomalySeverity.CRITICAL,
        message="Campaign ROI is below the configured minimum threshold.",
        requires_human_review=True,
    )
    task_client = FakeTaskClient()
    workflow = _workflow(
        rows=[_row()],
        detector=RecordingDetector(findings=[finding, finding]),
        task_client=task_client,
        reports_dir=tmp_path,
    )

    result = await workflow.run()

    assert result.status is WorkflowStatus.NEEDS_APPROVAL
    assert len(task_client.requests) == 1
    assert len(result.created_tasks) == 1
    task_request = task_client.requests[0]
    assert task_request.title == "Review negative_roi for cmp-search-brand"
    assert task_request.campaign_id == "cmp-search-brand"
    assert "Campaign: cmp-search-brand" in task_request.description
    assert "Anomaly type: negative_roi" in task_request.description
    assert "Severity: critical" in task_request.description
    assert "Human review required: yes" in task_request.description


@pytest.mark.asyncio
async def test_healthy_campaigns_do_not_create_tasks(tmp_path: Path) -> None:
    task_client = FakeTaskClient()
    workflow = _workflow(
        rows=[_row()],
        detector=RecordingDetector(findings=[]),
        task_client=task_client,
        reports_dir=tmp_path,
    )

    result = await workflow.run()

    assert result.status is WorkflowStatus.SUCCEEDED
    assert task_client.requests == []
    assert result.created_tasks == ()


@pytest.mark.asyncio
async def test_partial_data_continues_through_data_quality_flags(
    tmp_path: Path,
) -> None:
    writer = RecordingReportWriter()
    workflow = _workflow(
        rows=[_row()],
        campaigns={},
        detector=AnomalyDetector(),
        report_writer=writer,
        reports_dir=tmp_path,
    )

    result = await workflow.run()

    assert result.status is WorkflowStatus.NEEDS_APPROVAL
    assert DataQualityFlag.MISSING_CAMPAIGN_METADATA in result.snapshots[0].data_quality_flags
    assert result.snapshots[0].campaign_metadata is None
    assert any(
        finding.anomaly_type is AnomalyType.MISSING_CAMPAIGN_METADATA
        for finding in result.findings
    )
    assert writer.received_snapshots == result.snapshots
    assert result.report_path.exists()


@pytest.mark.asyncio
async def test_unrecoverable_scraper_failure_is_surfaced_clearly(
    tmp_path: Path,
) -> None:
    workflow = _workflow(
        rows=[],
        scraper_error=DashboardUnavailableError("dashboard unavailable"),
        reports_dir=tmp_path,
    )

    with pytest.raises(WorkflowExecutionError) as exc_info:
        await workflow.run()

    assert exc_info.value.step == "scrape_marketing_panel"
    assert "dashboard unavailable" in str(exc_info.value)
    assert not list(tmp_path.iterdir())


def _workflow(
    *,
    rows: Sequence[ScrapedCampaignRow],
    campaigns: Mapping[str, Campaign] | None = None,
    metrics: Mapping[str, AnalyticsCampaignMetrics] | None = None,
    detector: RecordingDetector | AnomalyDetector | None = None,
    report_writer: RecordingReportWriter | None = None,
    task_client: FakeTaskClient | None = None,
    reports_dir: Path | str,
    scraper_error: Exception | None = None,
) -> DailyMarketingReportWorkflow:
    row = rows[0] if rows else _row()
    return DailyMarketingReportWorkflow(
        scraper=FakeScraper(rows, scraper_error),
        campaign_client=FakeCampaignClient(
            campaigns
            if campaigns is not None
            else {row.campaign_id: _campaign(campaign_id=row.campaign_id)}
        ),
        analytics_client=FakeAnalyticsClient(
            metrics
            if metrics is not None
            else {row.campaign_id: _analytics(campaign_id=row.campaign_id)}
        ),
        detector=detector or RecordingDetector(findings=[]),
        report_writer=report_writer or RecordingReportWriter(),
        task_client=task_client,
        reports_dir=reports_dir,
        clock=lambda: REFERENCE_TIME,
    )


def _row(
    *,
    campaign_id: str = "cmp-search-brand",
    name: str = "Brand Search Defense",
    channel: Channel = Channel.SEARCH,
    conversions: int = 640,
    cost: float = 12_150.0,
    revenue: float = 38_400.0,
) -> ScrapedCampaignRow:
    return ScrapedCampaignRow(
        campaign_id=campaign_id,
        name=name,
        channel=channel,
        impressions=120_000,
        clicks=8_200,
        conversions=conversions,
        cost=cost,
        revenue=revenue,
    )


def _campaign(*, campaign_id: str = "cmp-search-brand") -> Campaign:
    return Campaign(
        campaign_id=campaign_id,
        name="Brand Search Defense",
        channel=Channel.SEARCH,
        metrics=CampaignMetrics(
            impressions=120_000,
            clicks=8_200,
            conversions=640,
            spend=12_150.0,
            revenue=38_400.0,
        ),
        collected_at=REFERENCE_TIME,
    )


def _analytics(*, campaign_id: str = "cmp-search-brand") -> AnalyticsCampaignMetrics:
    return AnalyticsCampaignMetrics(
        campaignId=campaign_id,
        impressions=120_000,
        clicks=8_200,
        conversions=640,
        revenue=38_400.0,
        cost=12_150.0,
    )


def _finding(
    *,
    anomaly_type: AnomalyType,
    severity: AnomalySeverity,
    message: str,
    requires_human_review: bool = False,
) -> AnomalyFinding:
    return AnomalyFinding(
        campaign_id="cmp-search-brand",
        anomaly_type=anomaly_type,
        severity=severity,
        message=message,
        source="marketing_panel",
        source_evidence={
            "panel_spend": 12_150.0,
            "panel_conversions": 640,
        },
        requires_human_review=requires_human_review,
    )
