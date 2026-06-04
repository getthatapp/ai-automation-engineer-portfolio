"""Deterministic timeline generation for local AgentOps evidence."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from agentops_control_tower.models import (
    AgentOpsTimeline,
    AgentOpsTimelineEvent,
    ApprovalRequestRecord,
    GuardrailEvidenceRecord,
    GuardrailStatus,
    IngestionError,
    IngestionResult,
    IngestionSourceType,
    IngestionWarning,
    ReportSummaryRecord,
    SummarySeverity,
    TimelineEventType,
    ToolEvidenceRecord,
    WorkflowRunRecord,
    WorkflowStatus,
)

_EVENT_TYPE_ORDER: dict[TimelineEventType, int] = {
    event_type: index for index, event_type in enumerate(TimelineEventType)
}


def build_agentops_timeline(ingestion_result: IngestionResult) -> AgentOpsTimeline:
    """Build a deterministic timeline from local ingestion output.

    Args:
        ingestion_result: Typed ingestion result from local parsers.

    Returns:
        Timeline with stable ordering and no inferred timestamps.
    """
    events: list[AgentOpsTimelineEvent] = []
    for record in ingestion_result.records:
        if isinstance(record, WorkflowRunRecord):
            events.append(_workflow_event(record))
        elif isinstance(record, ApprovalRequestRecord):
            events.append(_approval_event(record))
        elif isinstance(record, ReportSummaryRecord):
            events.append(_report_event(record))
        elif isinstance(record, ToolEvidenceRecord):
            events.append(_tool_event(record))
        elif isinstance(record, GuardrailEvidenceRecord):
            events.append(_guardrail_event(record))

    events.extend(
        _warning_event(warning, index)
        for index, warning in enumerate(ingestion_result.warnings)
    )
    events.extend(_error_event(error, index) for index, error in enumerate(ingestion_result.errors))
    return AgentOpsTimeline(events=tuple(sorted(events, key=_event_sort_key)))


def _workflow_event(record: WorkflowRunRecord) -> AgentOpsTimelineEvent:
    """Build a timeline event from a workflow run record.

    Args:
        record: Workflow run record.

    Returns:
        Timeline event.
    """
    severity = (
        SummarySeverity.ERROR
        if record.status is WorkflowStatus.FAILED
        else SummarySeverity.HEALTHY
    )
    if record.status is WorkflowStatus.NEEDS_APPROVAL or record.human_review_required:
        severity = SummarySeverity.NEEDS_ATTENTION
    return AgentOpsTimelineEvent(
        event_type=TimelineEventType.WORKFLOW_RUN,
        source_type=IngestionSourceType.RUN_HISTORY,
        identifier=record.run_id,
        title=f"Workflow run {record.run_id}",
        timestamp=record.started_at,
        severity=severity,
        details={
            "workflow_name": record.workflow_name,
            "status": record.status.value,
            "finding_count": record.finding_count,
            "critical_finding_count": record.critical_finding_count,
            "human_review_required": record.human_review_required,
        },
    )


def _approval_event(record: ApprovalRequestRecord) -> AgentOpsTimelineEvent:
    """Build a timeline event from an approval request record.

    Args:
        record: Approval request record.

    Returns:
        Timeline event.
    """
    severity = (
        SummarySeverity.NEEDS_ATTENTION
        if record.status.value == "pending"
        else SummarySeverity.HEALTHY
    )
    return AgentOpsTimelineEvent(
        event_type=TimelineEventType.APPROVAL_REQUEST,
        source_type=IngestionSourceType.APPROVAL_REQUESTS,
        identifier=record.approval_id,
        title=record.title or f"Approval request {record.approval_id}",
        timestamp=record.created_at,
        severity=severity,
        details={
            "status": record.status.value,
            "risk_level": record.risk_level,
            "run_id": record.run_id,
            "campaign_id": record.campaign_id,
        },
    )


def _report_event(record: ReportSummaryRecord) -> AgentOpsTimelineEvent:
    """Build a timeline event from a report summary record.

    Args:
        record: Report summary record.

    Returns:
        Timeline event.
    """
    requires_review = (record.campaigns_requiring_human_review or 0) > 0
    return AgentOpsTimelineEvent(
        event_type=TimelineEventType.REPORT_SUMMARY,
        source_type=IngestionSourceType.MARKDOWN_REPORT,
        identifier=str(record.path),
        title=f"Report summary {record.path.name}",
        timestamp=record.generated_timestamp,
        severity=SummarySeverity.NEEDS_ATTENTION if requires_review else SummarySeverity.HEALTHY,
        details={
            "campaigns_processed": record.campaigns_processed,
            "critical_findings": record.critical_findings,
            "warning_findings": record.warning_findings,
            "campaigns_requiring_human_review": record.campaigns_requiring_human_review,
        },
    )


def _tool_event(record: ToolEvidenceRecord) -> AgentOpsTimelineEvent:
    """Build a timeline event from saved tool evidence.

    Args:
        record: Tool evidence record.

    Returns:
        Timeline event.
    """
    severity = SummarySeverity.WARNING if record.ready is False else SummarySeverity.HEALTHY
    return AgentOpsTimelineEvent(
        event_type=TimelineEventType.TOOL_EVIDENCE,
        source_type=IngestionSourceType.TOOL_EVIDENCE,
        identifier=str(record.path),
        title=f"Tool evidence {record.tool_name or record.path.name}",
        severity=severity,
        details={
            "tool_name": record.tool_name,
            "status": record.status,
            "ready": record.ready,
        },
    )


def _guardrail_event(record: GuardrailEvidenceRecord) -> AgentOpsTimelineEvent:
    """Build a timeline event from guardrail output.

    Args:
        record: Guardrail evidence record.

    Returns:
        Timeline event.
    """
    severity = SummarySeverity.HEALTHY
    if record.status in {GuardrailStatus.FAILED, GuardrailStatus.BLOCKED}:
        severity = SummarySeverity.NEEDS_ATTENTION
    elif record.status is GuardrailStatus.UNKNOWN:
        severity = SummarySeverity.WARNING
    return AgentOpsTimelineEvent(
        event_type=TimelineEventType.GUARDRAIL_EVIDENCE,
        source_type=IngestionSourceType.GUARDRAIL_OUTPUT,
        identifier=str(record.path),
        title=f"Guardrail output {record.path.name}",
        severity=severity,
        details={
            "status": record.status.value,
            "matched_signals": list(record.matched_signals),
            "line_count": record.line_count,
        },
    )


def _warning_event(warning: IngestionWarning, index: int) -> AgentOpsTimelineEvent:
    """Build a timeline event from an ingestion warning.

    Args:
        warning: Ingestion warning.
        index: Stable warning index from the ingestion result.

    Returns:
        Timeline event.
    """
    identifier = f"{warning.source_type.value}:warning:{index}:{_path_text(warning.path)}"
    return AgentOpsTimelineEvent(
        event_type=TimelineEventType.INGESTION_WARNING,
        source_type=warning.source_type,
        identifier=identifier,
        title=f"Ingestion warning: {warning.code}",
        severity=SummarySeverity.WARNING,
        details={
            "code": warning.code,
            "message": warning.message,
            "path": _path_text(warning.path),
        },
    )


def _error_event(error: IngestionError, index: int) -> AgentOpsTimelineEvent:
    """Build a timeline event from an ingestion error.

    Args:
        error: Ingestion error.
        index: Stable error index from the ingestion result.

    Returns:
        Timeline event.
    """
    identifier = f"{error.source_type.value}:error:{index}:{_path_text(error.path)}"
    return AgentOpsTimelineEvent(
        event_type=TimelineEventType.INGESTION_ERROR,
        source_type=error.source_type,
        identifier=identifier,
        title=f"Ingestion error: {error.code}",
        severity=SummarySeverity.ERROR,
        details={
            "code": error.code,
            "message": error.message,
            "line_number": error.line_number,
            "path": _path_text(error.path),
        },
    )


def _event_sort_key(event: AgentOpsTimelineEvent) -> tuple[bool, datetime | str, int, str, str]:
    """Return the deterministic timeline sort key for an event.

    Args:
        event: Timeline event.

    Returns:
        Sort key placing timestamped events before untimestamped events.
    """
    timestamp_key: datetime | str = event.timestamp if event.timestamp is not None else ""
    return (
        event.timestamp is None,
        timestamp_key,
        _EVENT_TYPE_ORDER[event.event_type],
        event.source_type.value,
        event.identifier,
    )


def _path_text(path: Path | None) -> str:
    """Return stable text for an optional path.

    Args:
        path: Optional local path.

    Returns:
        Path text or an empty string.
    """
    return "" if path is None else str(path)
