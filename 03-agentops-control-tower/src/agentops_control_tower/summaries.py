"""Deterministic AgentOps summaries over local ingestion results."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from agentops_control_tower.ingestion import ingest_local_agentops_sources
from agentops_control_tower.models import (
    AgentOpsControlTowerView,
    AgentOpsSummary,
    ApprovalRequestRecord,
    ApprovalStatus,
    ApprovalSummary,
    GuardrailEvidenceRecord,
    GuardrailStatus,
    GuardrailSummary,
    IngestionResult,
    ReportHealthSummary,
    ReportSummaryRecord,
    SummarySeverity,
    ToolEvidenceRecord,
    ToolEvidenceSummary,
    WorkflowRunRecord,
    WorkflowRunSummary,
    WorkflowStatus,
)
from agentops_control_tower.timeline import build_agentops_timeline


def build_agentops_summary(ingestion_result: IngestionResult) -> AgentOpsSummary:
    """Build a deterministic local AgentOps summary.

    Args:
        ingestion_result: Typed ingestion result from local parsers.

    Returns:
        Dashboard-ready local summary.
    """
    workflow_summary = _workflow_summary(_workflow_records(ingestion_result))
    approval_summary = _approval_summary(_approval_records(ingestion_result))
    report_summary = _report_summary(_report_records(ingestion_result))
    tool_summary = _tool_summary(_tool_records(ingestion_result))
    guardrail_summary = _guardrail_summary(_guardrail_records(ingestion_result))
    warning_count = len(ingestion_result.warnings)
    error_count = len(ingestion_result.errors)
    overall_status = _overall_status(
        workflow_summary,
        approval_summary,
        report_summary,
        guardrail_summary,
        warning_count,
        error_count,
    )
    return AgentOpsSummary(
        overall_status=overall_status,
        workflow_runs=workflow_summary,
        approvals=approval_summary,
        reports=report_summary,
        tools=tool_summary,
        guardrails=guardrail_summary,
        ingestion_warning_count=warning_count,
        ingestion_error_count=error_count,
        recommended_actions=_recommended_actions(
            overall_status,
            workflow_summary,
            approval_summary,
            report_summary,
            guardrail_summary,
            warning_count,
            error_count,
        ),
    )


def build_agentops_control_tower_view(
    *,
    ingestion_result: IngestionResult | None = None,
    run_history_path: str | Path | None = None,
    approval_requests_path: str | Path | None = None,
    markdown_report_path: str | Path | None = None,
    tool_evidence_json_path: str | Path | None = None,
    guardrail_output_text_path: str | Path | None = None,
    run_history_limit: int | None = None,
    approval_status_filter: ApprovalStatus | str | None = None,
) -> AgentOpsControlTowerView:
    """Build a combined local ingestion, summary and timeline view.

    Args:
        ingestion_result: Optional existing ingestion result. When provided,
            path arguments are ignored.
        run_history_path: Optional Project 1 run-history JSONL path.
        approval_requests_path: Optional Project 1 approval requests JSONL path.
        markdown_report_path: Optional Project 1 Markdown report path.
        tool_evidence_json_path: Optional saved Project 2 CLI JSON evidence path.
        guardrail_output_text_path: Optional saved Project 2 guardrail output path.
        run_history_limit: Optional run-history record limit.
        approval_status_filter: Optional approval status filter.

    Returns:
        Combined AgentOps control tower view.
    """
    resolved_ingestion = ingestion_result or ingest_local_agentops_sources(
        run_history_path=run_history_path,
        approval_requests_path=approval_requests_path,
        markdown_report_path=markdown_report_path,
        tool_evidence_json_path=tool_evidence_json_path,
        guardrail_output_text_path=guardrail_output_text_path,
        run_history_limit=run_history_limit,
        approval_status_filter=approval_status_filter,
    )
    return AgentOpsControlTowerView(
        ingestion_result=resolved_ingestion,
        summary=build_agentops_summary(resolved_ingestion),
        timeline=build_agentops_timeline(resolved_ingestion),
    )


def _workflow_summary(records: tuple[WorkflowRunRecord, ...]) -> WorkflowRunSummary:
    """Build workflow run summary counts.

    Args:
        records: Workflow run records.

    Returns:
        Workflow run summary.
    """
    by_status = _count_by_status(tuple(WorkflowStatus), [record.status for record in records])
    return WorkflowRunSummary(
        total=len(records),
        by_status=by_status,
        failed_count=by_status[WorkflowStatus.FAILED],
        human_review_required_count=sum(1 for record in records if record.human_review_required),
    )


def _approval_summary(records: tuple[ApprovalRequestRecord, ...]) -> ApprovalSummary:
    """Build approval request summary counts.

    Args:
        records: Approval request records.

    Returns:
        Approval request summary.
    """
    by_status = _count_by_status(tuple(ApprovalStatus), [record.status for record in records])
    return ApprovalSummary(
        total=len(records),
        by_status=by_status,
        pending_count=by_status[ApprovalStatus.PENDING],
    )


def _report_summary(records: tuple[ReportSummaryRecord, ...]) -> ReportHealthSummary:
    """Build report health summary counts.

    Args:
        records: Report summary records.

    Returns:
        Report health summary.
    """
    return ReportHealthSummary(
        total=len(records),
        requiring_human_review_count=sum(
            1 for record in records if (record.campaigns_requiring_human_review or 0) > 0
        ),
        missing_required_section_count=sum(
            1
            for record in records
            if any(not present for present in record.required_sections.values())
        ),
    )


def _tool_summary(records: tuple[ToolEvidenceRecord, ...]) -> ToolEvidenceSummary:
    """Build local tool evidence summary counts.

    Args:
        records: Tool evidence records.

    Returns:
        Tool evidence summary.
    """
    return ToolEvidenceSummary(
        total=len(records),
        ready_count=sum(1 for record in records if record.ready is True),
        not_ready_count=sum(1 for record in records if record.ready is False),
    )


def _guardrail_summary(records: tuple[GuardrailEvidenceRecord, ...]) -> GuardrailSummary:
    """Build guardrail evidence summary counts.

    Args:
        records: Guardrail evidence records.

    Returns:
        Guardrail summary.
    """
    by_status = _count_by_status(tuple(GuardrailStatus), [record.status for record in records])
    return GuardrailSummary(
        total=len(records),
        by_status=by_status,
        failed_or_blocked_count=by_status[GuardrailStatus.FAILED]
        + by_status[GuardrailStatus.BLOCKED],
    )


def _overall_status(
    workflow_summary: WorkflowRunSummary,
    approval_summary: ApprovalSummary,
    report_summary: ReportHealthSummary,
    guardrail_summary: GuardrailSummary,
    warning_count: int,
    error_count: int,
) -> SummarySeverity:
    """Derive overall local health status.

    Args:
        workflow_summary: Workflow run summary.
        approval_summary: Approval request summary.
        report_summary: Report health summary.
        guardrail_summary: Guardrail summary.
        warning_count: Ingestion warning count.
        error_count: Ingestion error count.

    Returns:
        Overall deterministic status.
    """
    if error_count > 0:
        return SummarySeverity.ERROR
    if (
        guardrail_summary.failed_or_blocked_count > 0
        or approval_summary.pending_count > 0
        or workflow_summary.failed_count > 0
        or workflow_summary.human_review_required_count > 0
        or report_summary.requiring_human_review_count > 0
    ):
        return SummarySeverity.NEEDS_ATTENTION
    if (
        warning_count > 0
        or workflow_summary.by_status[WorkflowStatus.UNKNOWN] > 0
        or approval_summary.by_status[ApprovalStatus.UNKNOWN] > 0
        or guardrail_summary.by_status[GuardrailStatus.UNKNOWN] > 0
    ):
        return SummarySeverity.WARNING
    return SummarySeverity.HEALTHY


def _recommended_actions(
    overall_status: SummarySeverity,
    workflow_summary: WorkflowRunSummary,
    approval_summary: ApprovalSummary,
    report_summary: ReportHealthSummary,
    guardrail_summary: GuardrailSummary,
    warning_count: int,
    error_count: int,
) -> tuple[str, ...]:
    """Build deterministic local follow-up actions.

    Args:
        overall_status: Overall deterministic status.
        workflow_summary: Workflow run summary.
        approval_summary: Approval request summary.
        report_summary: Report health summary.
        guardrail_summary: Guardrail summary.
        warning_count: Ingestion warning count.
        error_count: Ingestion error count.

    Returns:
        Ordered recommended local actions.
    """
    actions: list[str] = []
    if error_count > 0:
        actions.append("Inspect malformed ingestion sources before using the summary.")
    if guardrail_summary.failed_or_blocked_count > 0:
        actions.append("Review failed or blocked guardrail output before continuing.")
    if workflow_summary.failed_count > 0:
        actions.append("Inspect failed workflow run records.")
    if approval_summary.pending_count > 0 or report_summary.requiring_human_review_count > 0:
        actions.append("Review pending approvals and human-review report findings.")
    if warning_count > 0 or report_summary.missing_required_section_count > 0:
        actions.append("Inspect ingestion warnings and incomplete report sections.")
    if overall_status is SummarySeverity.HEALTHY:
        actions.append("Continue monitoring local workflow evidence.")
    return tuple(actions)


def _workflow_records(ingestion_result: IngestionResult) -> tuple[WorkflowRunRecord, ...]:
    """Return workflow run records from an ingestion result.

    Args:
        ingestion_result: Source ingestion result.

    Returns:
        Workflow run records.
    """
    return tuple(
        record for record in ingestion_result.records if isinstance(record, WorkflowRunRecord)
    )


def _approval_records(ingestion_result: IngestionResult) -> tuple[ApprovalRequestRecord, ...]:
    """Return approval request records from an ingestion result.

    Args:
        ingestion_result: Source ingestion result.

    Returns:
        Approval request records.
    """
    return tuple(
        record for record in ingestion_result.records if isinstance(record, ApprovalRequestRecord)
    )


def _report_records(ingestion_result: IngestionResult) -> tuple[ReportSummaryRecord, ...]:
    """Return report summary records from an ingestion result.

    Args:
        ingestion_result: Source ingestion result.

    Returns:
        Report summary records.
    """
    return tuple(
        record for record in ingestion_result.records if isinstance(record, ReportSummaryRecord)
    )


def _tool_records(ingestion_result: IngestionResult) -> tuple[ToolEvidenceRecord, ...]:
    """Return tool evidence records from an ingestion result.

    Args:
        ingestion_result: Source ingestion result.

    Returns:
        Tool evidence records.
    """
    return tuple(
        record for record in ingestion_result.records if isinstance(record, ToolEvidenceRecord)
    )


def _guardrail_records(ingestion_result: IngestionResult) -> tuple[GuardrailEvidenceRecord, ...]:
    """Return guardrail evidence records from an ingestion result.

    Args:
        ingestion_result: Source ingestion result.

    Returns:
        Guardrail evidence records.
    """
    return tuple(
        record for record in ingestion_result.records if isinstance(record, GuardrailEvidenceRecord)
    )


def _count_by_status[StatusT](
    members: Sequence[StatusT],
    values: list[StatusT],
) -> dict[StatusT, int]:
    """Count enum status values while preserving every enum member.

    Args:
        members: Status values to initialize.
        values: Status values to count.

    Returns:
        Mapping with every enum member initialized.
    """
    counts = {status: 0 for status in members}
    for value in values:
        counts[value] += 1
    return counts
