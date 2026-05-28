"""Deterministic daily marketing report workflow orchestration."""

import asyncio
import logging
from collections import Counter
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
from marketing_ops_agent.approval import (
    DEFAULT_APPROVAL_RECORDS_PATH,
    ApprovalRequest,
    ApprovalService,
    LocalApprovalStore,
)
from marketing_ops_agent.browser import PlaywrightMarketingPanelScraper, ScrapedCampaignRow
from marketing_ops_agent.clients import (
    AnalyticsClient,
    CampaignClient,
    ProjectManagementClient,
    ProjectTask,
    ProjectTaskCreate,
    ServiceClientError,
)
from marketing_ops_agent.config import load_config
from marketing_ops_agent.llm import (
    DeterministicMockLLMProvider,
    LLMInterpretationRequest,
    LLMInterpretationResult,
    LLMInterpreter,
)
from marketing_ops_agent.models import WorkflowStatus
from marketing_ops_agent.observability import (
    DEFAULT_RUN_RECORDS_PATH,
    LocalRunRecorder,
    WorkflowRunRecord,
)
from marketing_ops_agent.reporting import MarkdownReportWriter, ReportMetadata, sort_findings
from marketing_ops_agent.workflows.models import DailyMarketingReportResult

DEFAULT_REPORTS_DIR = Path("reports")
REPORT_FILENAME_PREFIX = "daily-marketing-report"
WORKFLOW_NAME = "daily_marketing_report"

logger = logging.getLogger(__name__)


class MarketingPanelScraper(Protocol):
    """Scraper contract needed by the workflow."""

    async def scrape_campaign_rows(self) -> list[ScrapedCampaignRow]:
        """Scrape campaign rows from the marketing panel.

        Returns:
            Validated scraped campaign rows.
        """
        ...


class CampaignAnomalyDetector(Protocol):
    """Detector contract needed by the workflow."""

    def detect(self, snapshots: Sequence[CampaignSnapshot]) -> list[AnomalyFinding]:
        """Detect deterministic anomalies from campaign snapshots.

        Args:
            snapshots: Aggregated campaign snapshots.

        Returns:
            Deterministic anomaly findings.
        """
        ...


class CampaignReportWriter(Protocol):
    """Report writer contract needed by the workflow."""

    def write(
        self,
        snapshots: Sequence[CampaignSnapshot],
        findings: Sequence[AnomalyFinding],
        metadata: ReportMetadata | None = None,
    ) -> str:
        """Render a deterministic report from snapshots and findings.

        Args:
            snapshots: Aggregated campaign snapshots.
            findings: Deterministic anomaly findings.
            metadata: Optional report metadata.

        Returns:
            Markdown report text.
        """
        ...


class TaskCreationClient(Protocol):
    """Project management task client contract needed by the workflow."""

    async def create_task(self, task: ProjectTaskCreate) -> ProjectTask:
        """Create a project management task.

        Args:
            task: Validated task creation request.

        Returns:
            Created project task.
        """
        ...


class WorkflowRunRecorder(Protocol):
    """Persistent recorder contract needed by the workflow."""

    def append(self, record: WorkflowRunRecord) -> None:
        """Persist one workflow run record.

        Args:
            record: Validated workflow run record.

        Side Effects:
            May write to durable local or remote storage.
        """
        ...


class WorkflowLLMInterpreter(Protocol):
    """Optional LLM interpreter contract needed by the workflow."""

    async def interpret(
        self,
        request: LLMInterpretationRequest,
    ) -> LLMInterpretationResult:
        """Interpret deterministic workflow outputs with an optional LLM layer.

        Args:
            request: Validated LLM interpretation request.

        Returns:
            Structured LLM interpretation result.
        """
        ...


class WorkflowApprovalService(Protocol):
    """Approval request service contract needed by the workflow."""

    def create_requests_for_run(
        self,
        *,
        run_id: str | None,
        findings: Sequence[AnomalyFinding],
        llm_interpretation: LLMInterpretationResult | None = None,
    ) -> list[ApprovalRequest]:
        """Create approval requests for high-risk workflow outputs.

        Args:
            run_id: Optional workflow run identifier.
            findings: Deterministic anomaly findings.
            llm_interpretation: Optional structured LLM interpretation.

        Returns:
            Persisted approval requests.
        """
        ...


class WorkflowExecutionError(Exception):
    """Raised when an unrecoverable workflow step fails."""

    def __init__(self, step: str, cause: BaseException) -> None:
        """Initialize the workflow error with failed step context.

        Args:
            step: Workflow step name that failed.
            cause: Original exception raised by the step.
        """
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
        llm_interpreter: WorkflowLLMInterpreter | None = None,
        approval_service: WorkflowApprovalService | None = None,
        task_client: TaskCreationClient | None = None,
        run_recorder: WorkflowRunRecorder | None = None,
        reports_dir: Path | str = DEFAULT_REPORTS_DIR,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        """Initialize workflow dependencies and local output settings.

        Args:
            scraper: Browser or fake scraper boundary.
            campaign_client: Campaign REST API metadata boundary.
            analytics_client: Analytics GraphQL metrics boundary.
            detector: Optional anomaly detector override.
            report_writer: Optional deterministic report writer override.
            llm_interpreter: Optional non-blocking LLM interpretation boundary.
            approval_service: Optional non-blocking human approval boundary.
            task_client: Optional project management task boundary.
            run_recorder: Optional workflow run recorder.
            reports_dir: Directory where Markdown reports are written.
            clock: Optional clock used for deterministic timestamps.
        """
        self._scraper = scraper
        self._aggregator = CampaignAggregator(
            campaign_client=campaign_client,
            analytics_client=analytics_client,
        )
        self._detector = detector or AnomalyDetector()
        self._report_writer = report_writer or MarkdownReportWriter()
        self._llm_interpreter = llm_interpreter
        self._approval_service = approval_service
        self._task_client = task_client
        self._run_recorder = run_recorder
        self._reports_dir = Path(reports_dir)
        self._clock = clock or (lambda: datetime.now(UTC))

    async def run(self) -> DailyMarketingReportResult:
        """Run the deterministic workflow and return a typed result.

        Returns:
            Auditable workflow result with report path, counts and optional LLM
            interpretation.

        Raises:
            WorkflowExecutionError: If an unrecoverable workflow step fails.

        Side Effects:
            Scrapes the panel, calls mock APIs, writes a Markdown report, may
            call an LLM interpreter, may create project tasks and may append a
            JSONL run record.
        """

        started_at = self._normalize_datetime(self._clock())
        run_id = _run_id(started_at)
        logger.info("Starting daily marketing report workflow run %s", run_id)
        snapshots: list[CampaignSnapshot] = []
        findings: list[AnomalyFinding] = []
        report_path: Path | None = None
        llm_interpretation: LLMInterpretationResult | None = None
        approval_requests: list[ApprovalRequest] = []
        created_tasks: list[ProjectTask] = []
        task_errors: list[str] = []

        try:
            scraped_rows = await self._scrape_rows()
            snapshots = await self._aggregate_snapshots(scraped_rows, started_at)
            findings = self._detect_findings(snapshots)
            report_markdown = self._write_report(snapshots, findings, started_at)
            report_path = self._save_report(report_markdown, started_at)
            llm_interpretation = await self._interpret_report_safely(
                snapshots,
                findings,
                report_markdown,
            )
            approval_requests = self._create_approval_requests_safely(
                run_id=run_id,
                findings=findings,
                llm_interpretation=llm_interpretation,
            )
            created_tasks, task_errors = await self._create_tasks(findings)
        except WorkflowExecutionError as exc:
            finished_at = self._normalize_datetime(self._clock())
            self._record_run_safely(
                _build_failed_run_record(
                    run_id=run_id,
                    started_at=started_at,
                    finished_at=finished_at,
                    snapshots=snapshots,
                    findings=findings,
                    report_path=report_path,
                    approval_requests=approval_requests,
                    created_tasks=created_tasks,
                    task_errors=task_errors,
                    error=exc,
                )
            )
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
            llm_interpretation=llm_interpretation,
            approval_request_ids=tuple(
                request.approval_id for request in approval_requests
            ),
            created_tasks=tuple(created_tasks),
            task_creation_errors=tuple(task_errors),
        )
        self._record_run_safely(_build_success_run_record(result))
        logger.info(
            "Daily marketing report workflow run %s finished with status %s",
            run_id,
            result.status,
        )
        return result

    async def _scrape_rows(self) -> list[ScrapedCampaignRow]:
        """Scrape panel rows and wrap scraper failures with workflow context.

        Returns:
            Validated scraped campaign rows.

        Raises:
            WorkflowExecutionError: If browser scraping fails.
        """
        try:
            return await self._scraper.scrape_campaign_rows()
        except Exception as exc:
            raise WorkflowExecutionError("scrape_marketing_panel", exc) from exc

    async def _aggregate_snapshots(
        self,
        scraped_rows: Sequence[ScrapedCampaignRow],
        reference_time: datetime,
    ) -> list[CampaignSnapshot]:
        """Aggregate scraped rows into campaign snapshots.

        Args:
            scraped_rows: Rows scraped from the marketing panel.
            reference_time: Timestamp used for aggregation and stale checks.

        Returns:
            Aggregated campaign snapshots.

        Raises:
            WorkflowExecutionError: If aggregation fails.
        """
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
        """Detect deterministic findings from snapshots.

        Args:
            snapshots: Aggregated campaign snapshots.

        Returns:
            Deterministic anomaly findings.

        Raises:
            WorkflowExecutionError: If anomaly detection fails.
        """
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
        """Render the deterministic Markdown report.

        Args:
            snapshots: Aggregated campaign snapshots.
            findings: Deterministic anomaly findings.
            generated_at: Report generation timestamp.

        Returns:
            Markdown report text.

        Raises:
            WorkflowExecutionError: If report rendering fails.
        """
        metadata = ReportMetadata(generated_at=generated_at)
        try:
            return self._report_writer.write(snapshots, findings, metadata)
        except Exception as exc:
            raise WorkflowExecutionError("write_markdown_report", exc) from exc

    def _save_report(self, report_markdown: str, generated_at: datetime) -> Path:
        """Write the deterministic Markdown report to disk.

        Args:
            report_markdown: Report content to persist.
            generated_at: Timestamp used to build the report filename.

        Returns:
            Local report path.

        Raises:
            WorkflowExecutionError: If the report cannot be written.

        Side Effects:
            Creates the reports directory and writes a Markdown file.
        """
        report_path = self._report_path(generated_at)
        try:
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(report_markdown, encoding="utf-8")
        except OSError as exc:
            raise WorkflowExecutionError("save_markdown_report", exc) from exc
        return report_path

    async def _interpret_report_safely(
        self,
        snapshots: Sequence[CampaignSnapshot],
        findings: Sequence[AnomalyFinding],
        report_markdown: str,
    ) -> LLMInterpretationResult | None:
        """Run optional LLM interpretation without blocking the workflow.

        Args:
            snapshots: Aggregated campaign snapshots.
            findings: Deterministic anomaly findings.
            report_markdown: Deterministic report text.

        Returns:
            LLM interpretation result, or `None` when disabled or failed.

        Side Effects:
            May call the configured LLM interpreter and logs unexpected errors.
        """
        if self._llm_interpreter is None:
            return None

        request = LLMInterpretationRequest(
            snapshots=tuple(snapshots),
            findings=tuple(findings),
            deterministic_report_summary=report_markdown,
        )
        try:
            return await self._llm_interpreter.interpret(request)
        except Exception:
            logger.exception("Optional LLM interpretation failed without blocking workflow")
            return None

    async def _create_tasks(
        self,
        findings: Sequence[AnomalyFinding],
    ) -> tuple[list[ProjectTask], list[str]]:
        """Create deterministic follow-up tasks for critical/review findings.

        Args:
            findings: Deterministic anomaly findings.

        Returns:
            Created tasks and non-fatal task creation error messages.

        Side Effects:
            May call the project management API.
        """
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

    def _create_approval_requests_safely(
        self,
        *,
        run_id: str,
        findings: Sequence[AnomalyFinding],
        llm_interpretation: LLMInterpretationResult | None,
    ) -> list[ApprovalRequest]:
        """Create approval requests without blocking report generation.

        Args:
            run_id: Workflow run identifier.
            findings: Deterministic anomaly findings.
            llm_interpretation: Optional structured LLM interpretation.

        Returns:
            Approval requests created or found for this workflow run.

        Side Effects:
            May append approval records to local JSONL storage and logs
            persistence failures.
        """

        if self._approval_service is None:
            return []
        try:
            return self._approval_service.create_requests_for_run(
                run_id=run_id,
                findings=findings,
                llm_interpretation=llm_interpretation,
            )
        except Exception:
            logger.exception(
                "Optional approval request creation failed without blocking workflow"
            )
            return []

    def _report_path(self, generated_at: datetime) -> Path:
        """Build the timestamped Markdown report path."""
        return self._reports_dir / f"{REPORT_FILENAME_PREFIX}-{_timestamp_slug(generated_at)}.md"

    def _record_run_safely(self, record: WorkflowRunRecord) -> None:
        """Persist a workflow run record without changing workflow outcome.

        Args:
            record: Validated run record to persist.

        Side Effects:
            May append to JSONL run history and logs persistence failures.
        """
        if self._run_recorder is None:
            return
        try:
            self._run_recorder.append(record)
        except Exception:
            logger.exception(
                "Failed to persist workflow run record for %s",
                record.run_id,
            )

    @staticmethod
    def _normalize_datetime(value: datetime) -> datetime:
        """Normalize a datetime to UTC, treating naive values as UTC."""
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
    run_records_path: Path | str | None = DEFAULT_RUN_RECORDS_PATH,
    approval_records_path: Path | str | None = DEFAULT_APPROVAL_RECORDS_PATH,
    create_project_tasks: bool = False,
    enable_llm_interpretation: bool | None = None,
) -> DailyMarketingReportResult:
    """Run the workflow with concrete local scraper and service clients.

    Args:
        reports_dir: Directory where deterministic Markdown reports are written.
        run_records_path: Optional JSONL path for workflow run history.
        approval_records_path: Optional JSONL path for human approval records.
        create_project_tasks: Whether to create deterministic project tasks.
        enable_llm_interpretation: Optional override for LLM interpretation.

    Returns:
        Typed workflow result with report, task and approval metadata.

    Side Effects:
        Launches Playwright, calls mock services, writes a report, appends run
        history and may append approval requests or create project tasks.
    """

    config = load_config()
    llm_enabled = (
        config.llm_interpretation_enabled
        if enable_llm_interpretation is None
        else enable_llm_interpretation
    )

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
            llm_interpreter=(
                LLMInterpreter(
                    provider=DeterministicMockLLMProvider(
                        provider_name=config.llm_provider,
                        model_name=config.llm_model,
                    )
                )
                if llm_enabled
                else None
            ),
            approval_service=(
                ApprovalService(store=LocalApprovalStore(approval_records_path))
                if approval_records_path is not None
                else None
            ),
            run_recorder=(
                LocalRunRecorder(run_records_path)
                if run_records_path is not None
                else None
            ),
            reports_dir=reports_dir,
        )
        return await workflow.run()


def main() -> None:
    """Run the daily workflow from `python -m` and print the report path."""

    result = asyncio.run(run_daily_marketing_report_workflow())
    print(result.report_path)


def _should_create_task(finding: AnomalyFinding) -> bool:
    """Return whether a finding should create a deterministic task."""
    return finding.severity is AnomalySeverity.CRITICAL or finding.requires_human_review


def _task_description(finding: AnomalyFinding) -> str:
    """Build a deterministic project task description for one finding."""
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
    """Format sorted finding evidence for task descriptions."""
    if not finding.source_evidence:
        return "none"
    return "; ".join(
        f"{key}={_format_evidence_value(value)}"
        for key, value in sorted(finding.source_evidence.items())
    )


def _format_evidence_value(value: str | int | float | bool | None) -> str:
    """Format one evidence value for task descriptions."""
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
    """Return whether any snapshot or finding requires human review."""
    return any(snapshot.requires_human_review for snapshot in snapshots) or any(
        finding.requires_human_review for finding in findings
    )


def _format_bool(value: bool) -> str:
    """Format a boolean as yes or no."""
    return "yes" if value else "no"


def _timestamp_slug(value: datetime) -> str:
    """Format a datetime as a UTC timestamp slug for filenames."""
    normalized = value if value.tzinfo is not None else value.replace(tzinfo=UTC)
    return normalized.astimezone(UTC).strftime("%Y%m%dT%H%M%SZ")


def _run_id(started_at: datetime) -> str:
    """Build a deterministic workflow run ID from the start timestamp."""
    return f"{REPORT_FILENAME_PREFIX}-{_timestamp_slug(started_at)}"


def _build_success_run_record(
    result: DailyMarketingReportResult,
) -> WorkflowRunRecord:
    """Build a persisted run record for a successful workflow result."""
    return WorkflowRunRecord(
        run_id=result.run_id,
        workflow_name=WORKFLOW_NAME,
        status=result.status,
        started_at=result.started_at,
        finished_at=result.finished_at,
        duration_seconds=_duration_seconds(result.started_at, result.finished_at),
        report_path=result.report_path,
        snapshot_count=result.snapshot_count,
        finding_count=result.finding_count,
        critical_finding_count=_critical_finding_count(result.findings),
        human_review_required=result.requires_human_review,
        approval_request_count=len(result.approval_request_ids),
        created_task_ids=tuple(task.task_id for task in result.created_tasks),
        task_error_count=len(result.task_creation_errors),
        data_quality_summary=_data_quality_summary(result.snapshots),
        failure_type=None,
        failure_message=None,
    )


def _build_failed_run_record(
    *,
    run_id: str,
    started_at: datetime,
    finished_at: datetime,
    snapshots: Sequence[CampaignSnapshot],
    findings: Sequence[AnomalyFinding],
    report_path: Path | None,
    approval_requests: Sequence[ApprovalRequest],
    created_tasks: Sequence[ProjectTask],
    task_errors: Sequence[str],
    error: WorkflowExecutionError,
) -> WorkflowRunRecord:
    """Build a persisted run record for an unrecoverable workflow failure."""
    return WorkflowRunRecord(
        run_id=run_id,
        workflow_name=WORKFLOW_NAME,
        status=WorkflowStatus.FAILED,
        started_at=started_at,
        finished_at=finished_at,
        duration_seconds=_duration_seconds(started_at, finished_at),
        report_path=report_path,
        snapshot_count=len(snapshots),
        finding_count=len(findings),
        critical_finding_count=_critical_finding_count(findings),
        human_review_required=_requires_human_review(snapshots, findings),
        approval_request_count=len(approval_requests),
        created_task_ids=tuple(task.task_id for task in created_tasks),
        task_error_count=len(task_errors),
        data_quality_summary=_data_quality_summary(snapshots),
        failure_type=error.step,
        failure_message=str(error.cause),
    )


def _critical_finding_count(findings: Sequence[AnomalyFinding]) -> int:
    """Count critical deterministic findings."""
    return sum(1 for finding in findings if finding.severity is AnomalySeverity.CRITICAL)


def _data_quality_summary(snapshots: Sequence[CampaignSnapshot]) -> dict[str, int]:
    """Count data quality flags across campaign snapshots."""
    counts: Counter[str] = Counter(
        flag.value
        for snapshot in snapshots
        for flag in snapshot.data_quality_flags
    )
    return dict(sorted(counts.items()))


def _duration_seconds(started_at: datetime, finished_at: datetime) -> float:
    """Return non-negative workflow duration in seconds."""
    return max((finished_at - started_at).total_seconds(), 0.0)


if __name__ == "__main__":
    main()
