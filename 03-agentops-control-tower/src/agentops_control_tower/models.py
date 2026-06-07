"""Typed local observability records for AgentOps ingestion."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

SanitizedPayload = dict[str, Any]


class IngestionSourceType(StrEnum):
    """Supported local evidence source types."""

    RUN_HISTORY = "run_history"
    APPROVAL_REQUESTS = "approval_requests"
    MARKDOWN_REPORT = "markdown_report"
    TOOL_EVIDENCE = "tool_evidence"
    GUARDRAIL_OUTPUT = "guardrail_output"
    COMBINED = "combined"


class WorkflowStatus(StrEnum):
    """Workflow status values recognized by Project 3."""

    PENDING = "pending"
    RUNNING = "running"
    NEEDS_APPROVAL = "needs_approval"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    UNKNOWN = "unknown"


class ApprovalStatus(StrEnum):
    """Approval request lifecycle values recognized by Project 3."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    UNKNOWN = "unknown"


class GuardrailStatus(StrEnum):
    """Simple status values extracted from guardrail output text."""

    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"
    UNKNOWN = "unknown"


class TimelineEventType(StrEnum):
    """Dashboard-ready event categories produced from ingested evidence."""

    WORKFLOW_RUN = "workflow_run"
    APPROVAL_REQUEST = "approval_request"
    REPORT_SUMMARY = "report_summary"
    TOOL_EVIDENCE = "tool_evidence"
    GUARDRAIL_EVIDENCE = "guardrail_evidence"
    INGESTION_WARNING = "ingestion_warning"
    INGESTION_ERROR = "ingestion_error"


class SummarySeverity(StrEnum):
    """Overall local health severity for AgentOps summaries."""

    HEALTHY = "healthy"
    WARNING = "warning"
    NEEDS_ATTENTION = "needs_attention"
    ERROR = "error"


class IngestionWarning(BaseModel):
    """Non-fatal warning emitted while parsing local evidence."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    source_type: IngestionSourceType
    path: Path | None = None
    code: str = Field(min_length=1)
    message: str = Field(min_length=1)


class IngestionError(BaseModel):
    """User-facing ingestion error captured without leaking source secrets."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    source_type: IngestionSourceType
    path: Path | None = None
    code: str = Field(min_length=1)
    message: str = Field(min_length=1)
    line_number: int | None = Field(default=None, ge=1)


class WorkflowRunRecord(BaseModel):
    """Project 3 normalized summary of one workflow run-history record."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    run_id: str = Field(min_length=1)
    workflow_name: str = Field(default="unknown", min_length=1)
    status: WorkflowStatus = WorkflowStatus.UNKNOWN
    started_at: datetime | None = None
    finished_at: datetime | None = None
    duration_seconds: float | None = Field(default=None, ge=0)
    report_path: Path | None = None
    snapshot_count: int | None = Field(default=None, ge=0)
    finding_count: int | None = Field(default=None, ge=0)
    critical_finding_count: int | None = Field(default=None, ge=0)
    human_review_required: bool | None = None
    approval_request_count: int | None = Field(default=None, ge=0)
    notification_status: str | None = None
    notification_count: int | None = Field(default=None, ge=0)
    created_task_ids: tuple[str, ...] = ()
    task_error_count: int | None = Field(default=None, ge=0)
    data_quality_summary: SanitizedPayload = Field(default_factory=dict)
    failure_type: str | None = None
    failure_message: str | None = None
    raw: SanitizedPayload = Field(default_factory=dict)

    @field_validator("started_at", "finished_at")
    @classmethod
    def normalize_optional_datetime(cls, value: datetime | None) -> datetime | None:
        """Normalize optional timestamps to UTC.

        Args:
            value: Optional parsed timestamp.

        Returns:
            UTC-normalized timestamp or `None`.
        """
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)


class ApprovalRequestRecord(BaseModel):
    """Project 3 normalized summary of one approval request record."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    approval_id: str = Field(min_length=1)
    run_id: str | None = None
    campaign_id: str | None = None
    source: str | None = None
    source_reference: str | None = None
    risk_level: str | None = None
    status: ApprovalStatus = ApprovalStatus.UNKNOWN
    title: str | None = None
    rationale: str | None = None
    created_at: datetime | None = None
    decision: SanitizedPayload | None = None
    source_evidence: SanitizedPayload = Field(default_factory=dict)
    raw: SanitizedPayload = Field(default_factory=dict)

    @field_validator("created_at")
    @classmethod
    def normalize_created_at(cls, value: datetime | None) -> datetime | None:
        """Normalize optional approval creation timestamps to UTC.

        Args:
            value: Optional parsed timestamp.

        Returns:
            UTC-normalized timestamp or `None`.
        """
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)


class ReportSummaryRecord(BaseModel):
    """Project 3 normalized summary of one deterministic Markdown report."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    path: Path
    generated_timestamp: datetime | None = None
    campaigns_processed: int | None = Field(default=None, ge=0)
    critical_findings: int | None = Field(default=None, ge=0)
    warning_findings: int | None = Field(default=None, ge=0)
    campaigns_requiring_human_review: int | None = Field(default=None, ge=0)
    required_sections: dict[str, bool] = Field(default_factory=dict)

    @field_validator("generated_timestamp")
    @classmethod
    def normalize_generated_timestamp(cls, value: datetime | None) -> datetime | None:
        """Normalize optional report timestamps to UTC.

        Args:
            value: Optional generated timestamp.

        Returns:
            UTC-normalized timestamp or `None`.
        """
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)


class ToolEvidenceRecord(BaseModel):
    """Project 3 normalized summary of saved Project 2 CLI JSON evidence."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    path: Path
    tool_name: str | None = None
    status: str | None = None
    ready: bool | None = None
    payload: SanitizedPayload = Field(default_factory=dict)


class GuardrailEvidenceRecord(BaseModel):
    """Project 3 normalized summary of saved guardrail output text."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    path: Path
    status: GuardrailStatus = GuardrailStatus.UNKNOWN
    matched_signals: tuple[str, ...] = ()
    line_count: int = Field(ge=0)
    excerpt: str = ""


class IngestionResult(BaseModel):
    """Container for parsed local records, warnings and ingestion errors."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    source_type: IngestionSourceType
    records: tuple[
        WorkflowRunRecord
        | ApprovalRequestRecord
        | ReportSummaryRecord
        | ToolEvidenceRecord
        | GuardrailEvidenceRecord,
        ...,
    ] = ()
    warnings: tuple[IngestionWarning, ...] = ()
    errors: tuple[IngestionError, ...] = ()

    @property
    def ok(self) -> bool:
        """Return whether ingestion completed without typed errors.

        Returns:
            `True` when no errors were captured.
        """
        return not self.errors

    @property
    def record_count(self) -> int:
        """Return the number of parsed records.

        Returns:
            Count of records stored in this result.
        """
        return len(self.records)


class AgentOpsTimelineEvent(BaseModel):
    """One deterministic AgentOps timeline event derived from local evidence."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    event_type: TimelineEventType
    source_type: IngestionSourceType
    identifier: str = Field(min_length=1)
    title: str = Field(min_length=1)
    timestamp: datetime | None = None
    severity: SummarySeverity = SummarySeverity.HEALTHY
    details: SanitizedPayload = Field(default_factory=dict)

    @field_validator("timestamp")
    @classmethod
    def normalize_optional_timestamp(cls, value: datetime | None) -> datetime | None:
        """Normalize optional event timestamps to UTC.

        Args:
            value: Optional event timestamp.

        Returns:
            UTC-normalized timestamp or `None`.
        """
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)


class AgentOpsTimeline(BaseModel):
    """Deterministic timeline of local AgentOps evidence events."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    events: tuple[AgentOpsTimelineEvent, ...] = ()

    @property
    def event_count(self) -> int:
        """Return timeline event count.

        Returns:
            Number of timeline events.
        """
        return len(self.events)


class WorkflowRunSummary(BaseModel):
    """Summary counts for ingested workflow run records."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    total: int = Field(ge=0)
    by_status: dict[WorkflowStatus, int] = Field(default_factory=dict)
    failed_count: int = Field(ge=0)
    human_review_required_count: int = Field(ge=0)


class ApprovalSummary(BaseModel):
    """Summary counts for ingested approval request records."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    total: int = Field(ge=0)
    by_status: dict[ApprovalStatus, int] = Field(default_factory=dict)
    pending_count: int = Field(ge=0)


class ReportHealthSummary(BaseModel):
    """Summary counts for ingested deterministic report summaries."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    total: int = Field(ge=0)
    requiring_human_review_count: int = Field(ge=0)
    missing_required_section_count: int = Field(ge=0)


class ToolEvidenceSummary(BaseModel):
    """Summary counts for ingested local Project 2 tool evidence."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    total: int = Field(ge=0)
    ready_count: int = Field(ge=0)
    not_ready_count: int = Field(ge=0)


class GuardrailSummary(BaseModel):
    """Summary counts for ingested guardrail evidence records."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    total: int = Field(ge=0)
    by_status: dict[GuardrailStatus, int] = Field(default_factory=dict)
    failed_or_blocked_count: int = Field(ge=0)


class AgentOpsSummary(BaseModel):
    """Dashboard-ready deterministic summary over local AgentOps evidence."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    overall_status: SummarySeverity
    workflow_runs: WorkflowRunSummary
    approvals: ApprovalSummary
    reports: ReportHealthSummary
    tools: ToolEvidenceSummary
    guardrails: GuardrailSummary
    ingestion_warning_count: int = Field(ge=0)
    ingestion_error_count: int = Field(ge=0)
    recommended_actions: tuple[str, ...] = ()


class AgentOpsControlTowerView(BaseModel):
    """Combined local AgentOps ingestion, summary and timeline view."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    ingestion_result: IngestionResult
    summary: AgentOpsSummary
    timeline: AgentOpsTimeline
    input_paths: dict[IngestionSourceType, Path] = Field(default_factory=dict)
