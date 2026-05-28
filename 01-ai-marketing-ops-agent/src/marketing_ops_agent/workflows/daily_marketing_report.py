"""Deterministic daily marketing report workflow orchestration."""

import asyncio
import logging
from collections.abc import Callable, Sequence
from contextlib import AsyncExitStack
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol

from marketing_ops_agent.aggregation.aggregator import (
    CampaignAggregator,
    CampaignAnalyticsClient,
    CampaignMetadataClient,
)
from marketing_ops_agent.aggregation.campaign_snapshot import CampaignSnapshot
from marketing_ops_agent.anomaly import AnomalyDetector, AnomalyFinding, AnomalySeverity
from marketing_ops_agent.browser import PlaywrightMarketingPanelScraper, ScrapedCampaignRow
from marketing_ops_agent.clients import (
    AnalyticsClient,
    CampaignClient,
    ProjectManagementClient,
    ProjectTask,
    ProjectTaskCreate,
    ServiceClientError,
)
from marketing_ops_agent.models import WorkflowStatus
from marketing_ops_agent.reporting import MarkdownReportWriter, ReportMetadata, sort_findings
from marketing_ops_agent.workflows.models import DailyMarketingReportResult

DEFAULT_REPORTS_DIR = Path("reports")
REPORT_FILENAME_PREFIX = "daily-marketing-report"

logger = logging.getLogger(__name__)


class MarketingPanelScraper(Protocol):
    """Scraper contract needed by the workflow."""

    async def scrape_campaign_rows(self) -> list[ScrapedCampaignRow]: ...


class CampaignAnomalyDetector(Protocol):
    """Detector contract needed by the workflow."""

    def detect(self, snapshots: Sequence[CampaignSnapshot]) -> list[AnomalyFinding]: ...


class CampaignReportWriter(Protocol):
    """Report writer contract needed by the workflow."""

    def write(
        self,
        snapshots: Sequence[CampaignSnapshot],
        findings: Sequence[AnomalyFinding],
        metadata: ReportMetadata | None = None,
    ) -> str: ...


class TaskCreationClient(Protocol):
    """Project management task client contract needed by the workflow."""

    async def create_task(self, task: ProjectTaskCreate) -> ProjectTask: ...


class WorkflowExecutionError(Exception):
    """Raised when an unrecoverable workflow step fails."""

    def __init__(self, step: str, cause: BaseException) -> None:
        self.step = step
        self.cause = cause
        super().__init__(f"Daily marketing report workflow failed during {step}: {cause}")


class DailyMarketingReportWorkflow:
    """Execute the deterministic daily marketing report pipeline."""

    def __init__(
        self,
        *,
        scraper: MarketingPanelScraper,
        campaign_client: CampaignMetadataClient,
        analytics_client: CampaignAnalyticsClient,
        detector: CampaignAnomalyDetector | None = None,
        report_writer: CampaignReportWriter | None = None,
        task_client: TaskCreationClient | None = None,
        reports_dir: Path | str = DEFAULT_REPORTS_DIR,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._scraper = scraper
        self._aggregator = CampaignAggregator(
            campaign_client=campaign_client,
            analytics_client=analytics_client,
        )
        self._detector = detector or AnomalyDetector()
        self._report_writer = report_writer or MarkdownReportWriter()
        self._task_client = task_client
        self._reports_dir = Path(reports_dir)
        self._clock = clock or (lambda: datetime.now(UTC))

    async def run(self) -> DailyMarketingReportResult:
        """Run the deterministic workflow and return a typed result."""

        started_at = self._normalize_datetime(self._clock())
        run_id = _run_id(started_at)
        logger.info("Starting daily marketing report workflow run %s", run_id)

        try:
            scraped_rows = await self._scrape_rows()
            snapshots = await self._aggregate_snapshots(scraped_rows, started_at)
            findings = self._detect_findings(snapshots)
            report_markdown = self._write_report(snapshots, findings, started_at)
            report_path = self._save_report(report_markdown, started_at)
            created_tasks, task_errors = await self._create_tasks(findings)
        except WorkflowExecutionError:
            logger.exception("Daily marketing report workflow run %s failed", run_id)
            raise

        requires_human_review = _requires_human_review(snapshots, findings)
        finished_at = self._normalize_datetime(self._clock())
        status = (
            WorkflowStatus.NEEDS_APPROVAL
            if requires_human_review
            else WorkflowStatus.SUCCEEDED
        )
        result = DailyMarketingReportResult(
            run_id=run_id,
            status=status,
            started_at=started_at,
            finished_at=finished_at,
            report_path=report_path,
            scraped_rows_count=len(scraped_rows),
            snapshot_count=len(snapshots),
            finding_count=len(findings),
            requires_human_review=requires_human_review,
            snapshots=tuple(snapshots),
            findings=tuple(findings),
            created_tasks=tuple(created_tasks),
            task_creation_errors=tuple(task_errors),
        )
        logger.info(
            "Daily marketing report workflow run %s finished with status %s",
            run_id,
            result.status,
        )
        return result

    async def _scrape_rows(self) -> list[ScrapedCampaignRow]:
        try:
            return await self._scraper.scrape_campaign_rows()
        except Exception as exc:
            raise WorkflowExecutionError("scrape_marketing_panel", exc) from exc

    async def _aggregate_snapshots(
        self,
        scraped_rows: Sequence[ScrapedCampaignRow],
        reference_time: datetime,
    ) -> list[CampaignSnapshot]:
        try:
            return await self._aggregator.aggregate(
                scraped_rows,
                reference_time=reference_time,
            )
        except Exception as exc:
            raise WorkflowExecutionError("aggregate_campaign_data", exc) from exc

    def _detect_findings(
        self,
        snapshots: Sequence[CampaignSnapshot],
    ) -> list[AnomalyFinding]:
        try:
            return self._detector.detect(snapshots)
        except Exception as exc:
            raise WorkflowExecutionError("detect_anomalies", exc) from exc

    def _write_report(
        self,
        snapshots: Sequence[CampaignSnapshot],
        findings: Sequence[AnomalyFinding],
        generated_at: datetime,
    ) -> str:
        metadata = ReportMetadata(generated_at=generated_at)
        try:
            return self._report_writer.write(snapshots, findings, metadata)
        except Exception as exc:
            raise WorkflowExecutionError("write_markdown_report", exc) from exc

    def _save_report(self, report_markdown: str, generated_at: datetime) -> Path:
        report_path = self._report_path(generated_at)
        try:
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(report_markdown, encoding="utf-8")
        except OSError as exc:
            raise WorkflowExecutionError("save_markdown_report", exc) from exc
        return report_path

    async def _create_tasks(
        self,
        findings: Sequence[AnomalyFinding],
    ) -> tuple[list[ProjectTask], list[str]]:
        if self._task_client is None:
            return [], []

        created_tasks: list[ProjectTask] = []
        errors: list[str] = []
        for task_request in build_task_requests(findings):
            try:
                created_tasks.append(await self._task_client.create_task(task_request))
            except ServiceClientError as exc:
                errors.append(f"{task_request.campaign_id}: {exc}")
                logger.warning(
                    "Project task creation failed for campaign %s: %s",
                    task_request.campaign_id,
                    exc,
                )
        return created_tasks, errors

    def _report_path(self, generated_at: datetime) -> Path:
        return self._reports_dir / f"{REPORT_FILENAME_PREFIX}-{_timestamp_slug(generated_at)}.md"

    @staticmethod
    def _normalize_datetime(value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)


def build_task_requests(findings: Sequence[AnomalyFinding]) -> list[ProjectTaskCreate]:
    """Build deterministic task creation requests for critical or review findings."""

    task_requests: list[ProjectTaskCreate] = []
    seen_keys: set[tuple[str, str]] = set()
    for finding in sort_findings(findings):
        if not _should_create_task(finding):
            continue

        key = (finding.campaign_id, finding.anomaly_type.value)
        if key in seen_keys:
            continue

        seen_keys.add(key)
        task_requests.append(
            ProjectTaskCreate(
                title=(
                    f"Review {finding.anomaly_type.value} for "
                    f"{finding.campaign_id}"
                ),
                description=_task_description(finding),
                campaign_id=finding.campaign_id,
            )
        )
    return task_requests


async def run_daily_marketing_report_workflow(
    *,
    reports_dir: Path | str = DEFAULT_REPORTS_DIR,
    create_project_tasks: bool = False,
) -> DailyMarketingReportResult:
    """Run the workflow with concrete local scraper and service clients."""

    async with AsyncExitStack() as stack:
        scraper = await stack.enter_async_context(PlaywrightMarketingPanelScraper())
        campaign_client = await stack.enter_async_context(CampaignClient())
        analytics_client = await stack.enter_async_context(AnalyticsClient())
        task_client = (
            await stack.enter_async_context(ProjectManagementClient())
            if create_project_tasks
            else None
        )
        workflow = DailyMarketingReportWorkflow(
            scraper=scraper,
            campaign_client=campaign_client,
            analytics_client=analytics_client,
            task_client=task_client,
            reports_dir=reports_dir,
        )
        return await workflow.run()


def main() -> None:
    """Run the daily workflow from `python -m` and print the report path."""

    result = asyncio.run(run_daily_marketing_report_workflow())
    print(result.report_path)


def _should_create_task(finding: AnomalyFinding) -> bool:
    return finding.severity is AnomalySeverity.CRITICAL or finding.requires_human_review


def _task_description(finding: AnomalyFinding) -> str:
    lines = [
        f"Campaign: {finding.campaign_id}",
        f"Anomaly type: {finding.anomaly_type.value}",
        f"Severity: {finding.severity.value}",
        f"Human review required: {_format_bool(finding.requires_human_review)}",
        f"Source: {finding.source}",
        f"Finding: {finding.message}",
        f"Evidence: {_format_evidence(finding)}",
    ]
    description = "\n".join(lines)
    if len(description) <= 2_000:
        return description
    return f"{description[:1997]}..."


def _format_evidence(finding: AnomalyFinding) -> str:
    if not finding.source_evidence:
        return "none"
    return "; ".join(
        f"{key}={_format_evidence_value(value)}"
        for key, value in sorted(finding.source_evidence.items())
    )


def _format_evidence_value(value: str | int | float | bool | None) -> str:
    if value is None:
        return "missing"
    if isinstance(value, bool):
        return _format_bool(value)
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value).replace("\n", " ").replace("`", "'")


def _requires_human_review(
    snapshots: Sequence[CampaignSnapshot],
    findings: Sequence[AnomalyFinding],
) -> bool:
    return any(snapshot.requires_human_review for snapshot in snapshots) or any(
        finding.requires_human_review for finding in findings
    )


def _format_bool(value: bool) -> str:
    return "yes" if value else "no"


def _timestamp_slug(value: datetime) -> str:
    normalized = value if value.tzinfo is not None else value.replace(tzinfo=UTC)
    return normalized.astimezone(UTC).strftime("%Y%m%dT%H%M%SZ")


def _run_id(started_at: datetime) -> str:
    return f"{REPORT_FILENAME_PREFIX}-{_timestamp_slug(started_at)}"


if __name__ == "__main__":
    main()
