"""Tests for deterministic AgentOps summaries and timeline views."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

from agentops_control_tower.models import (
    AgentOpsTimelineEvent,
    ApprovalRequestRecord,
    ApprovalStatus,
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
from agentops_control_tower.summaries import (
    build_agentops_control_tower_view,
    build_agentops_summary,
)
from agentops_control_tower.timeline import build_agentops_timeline

REFERENCE_TIME = datetime(2026, 5, 28, 12, 0, tzinfo=UTC)


def test_timeline_from_workflow_run_records() -> None:
    """Build workflow timeline events from workflow run records."""
    result = IngestionResult(
        source_type=IngestionSourceType.COMBINED,
        records=(_workflow_run("run-001", status=WorkflowStatus.SUCCEEDED),),
    )

    timeline = build_agentops_timeline(result)

    event = timeline.events[0]
    assert event.event_type is TimelineEventType.WORKFLOW_RUN
    assert event.identifier == "run-001"
    assert event.timestamp == REFERENCE_TIME


def test_timeline_from_approval_records() -> None:
    """Build approval timeline events from approval request records."""
    result = IngestionResult(
        source_type=IngestionSourceType.COMBINED,
        records=(_approval("approval-001", status=ApprovalStatus.PENDING),),
    )

    event = build_agentops_timeline(result).events[0]

    assert event.event_type is TimelineEventType.APPROVAL_REQUEST
    assert event.identifier == "approval-001"
    assert event.severity is SummarySeverity.NEEDS_ATTENTION


def test_timeline_from_report_summaries() -> None:
    """Build report timeline events from report summary records."""
    result = IngestionResult(
        source_type=IngestionSourceType.COMBINED,
        records=(_report(Path("report.md"), human_review_count=1),),
    )

    event = build_agentops_timeline(result).events[0]

    assert event.event_type is TimelineEventType.REPORT_SUMMARY
    assert event.severity is SummarySeverity.NEEDS_ATTENTION


def test_timeline_from_tool_evidence_records() -> None:
    """Build tool evidence timeline events."""
    result = IngestionResult(
        source_type=IngestionSourceType.COMBINED,
        records=(
            ToolEvidenceRecord(
                path=Path("tool.json"),
                tool_name="check_runtime_clean",
                status="ok",
                ready=True,
                payload={"ready": True},
            ),
        ),
    )

    event = build_agentops_timeline(result).events[0]

    assert event.event_type is TimelineEventType.TOOL_EVIDENCE
    assert event.title == "Tool evidence check_runtime_clean"


def test_timeline_from_guardrail_evidence_records() -> None:
    """Build guardrail timeline events."""
    result = IngestionResult(
        source_type=IngestionSourceType.COMBINED,
        records=(
            GuardrailEvidenceRecord(
                path=Path("guardrail.txt"),
                status=GuardrailStatus.BLOCKED,
                matched_signals=("blocked",),
                line_count=1,
            ),
        ),
    )

    event = build_agentops_timeline(result).events[0]

    assert event.event_type is TimelineEventType.GUARDRAIL_EVIDENCE
    assert event.severity is SummarySeverity.NEEDS_ATTENTION


def test_warnings_and_errors_become_timeline_events() -> None:
    """Represent ingestion warnings and errors in the timeline."""
    result = IngestionResult(
        source_type=IngestionSourceType.COMBINED,
        warnings=(
            IngestionWarning(
                source_type=IngestionSourceType.MARKDOWN_REPORT,
                path=Path("missing.md"),
                code="missing_file",
                message="Optional ingestion source is missing.",
            ),
        ),
        errors=(
            IngestionError(
                source_type=IngestionSourceType.RUN_HISTORY,
                path=Path("workflow-runs.jsonl"),
                code="malformed_jsonl",
                message="JSONL line could not be decoded.",
                line_number=2,
            ),
        ),
    )

    events = build_agentops_timeline(result).events

    assert [event.event_type for event in events] == [
        TimelineEventType.INGESTION_WARNING,
        TimelineEventType.INGESTION_ERROR,
    ]


def test_timeline_ordering_is_deterministic() -> None:
    """Sort timestamped events first, then untimestamped events deterministically."""
    result = IngestionResult(
        source_type=IngestionSourceType.COMBINED,
        records=(
            ToolEvidenceRecord(path=Path("b-tool.json"), tool_name="b"),
            _workflow_run("run-late", started_at=REFERENCE_TIME + timedelta(minutes=5)),
            _approval("approval-early", created_at=REFERENCE_TIME - timedelta(minutes=5)),
            ToolEvidenceRecord(path=Path("a-tool.json"), tool_name="a"),
        ),
    )

    events = build_agentops_timeline(result).events

    assert [_event_key(event) for event in events] == [
        (TimelineEventType.APPROVAL_REQUEST, "approval-early"),
        (TimelineEventType.WORKFLOW_RUN, "run-late"),
        (TimelineEventType.TOOL_EVIDENCE, "a-tool.json"),
        (TimelineEventType.TOOL_EVIDENCE, "b-tool.json"),
    ]


def test_summary_counts_workflow_statuses() -> None:
    """Count workflow run statuses."""
    summary = build_agentops_summary(
        IngestionResult(
            source_type=IngestionSourceType.COMBINED,
            records=(
                _workflow_run("run-ok", status=WorkflowStatus.SUCCEEDED),
                _workflow_run("run-failed", status=WorkflowStatus.FAILED),
            ),
        )
    )

    assert summary.workflow_runs.total == 2
    assert summary.workflow_runs.by_status[WorkflowStatus.SUCCEEDED] == 1
    assert summary.workflow_runs.by_status[WorkflowStatus.FAILED] == 1


def test_summary_counts_approval_statuses() -> None:
    """Count approval request statuses."""
    summary = build_agentops_summary(
        IngestionResult(
            source_type=IngestionSourceType.COMBINED,
            records=(
                _approval("approval-pending", status=ApprovalStatus.PENDING),
                _approval("approval-approved", status=ApprovalStatus.APPROVED),
            ),
        )
    )

    assert summary.approvals.total == 2
    assert summary.approvals.pending_count == 1
    assert summary.approvals.by_status[ApprovalStatus.APPROVED] == 1


def test_summary_overall_status_healthy() -> None:
    """Derive healthy status when no warning signals exist."""
    summary = build_agentops_summary(
        IngestionResult(
            source_type=IngestionSourceType.COMBINED,
            records=(
                _workflow_run("run-ok", status=WorkflowStatus.SUCCEEDED),
                _approval("approval-approved", status=ApprovalStatus.APPROVED),
                _report(Path("report.md"), human_review_count=0),
                GuardrailEvidenceRecord(
                    path=Path("guardrail.txt"),
                    status=GuardrailStatus.PASSED,
                    matched_signals=("passed",),
                    line_count=1,
                ),
            ),
        )
    )

    assert summary.overall_status is SummarySeverity.HEALTHY


def test_summary_overall_status_warning() -> None:
    """Derive warning status from ingestion warnings."""
    summary = build_agentops_summary(
        IngestionResult(
            source_type=IngestionSourceType.COMBINED,
            warnings=(
                IngestionWarning(
                    source_type=IngestionSourceType.MARKDOWN_REPORT,
                    code="missing_file",
                    message="Optional source missing.",
                ),
            ),
        )
    )

    assert summary.overall_status is SummarySeverity.WARNING


def test_summary_overall_status_needs_attention() -> None:
    """Derive needs_attention status from pending approvals."""
    summary = build_agentops_summary(
        IngestionResult(
            source_type=IngestionSourceType.COMBINED,
            records=(_approval("approval-pending", status=ApprovalStatus.PENDING),),
        )
    )

    assert summary.overall_status is SummarySeverity.NEEDS_ATTENTION


def test_summary_overall_status_error() -> None:
    """Derive error status from ingestion errors."""
    summary = build_agentops_summary(
        IngestionResult(
            source_type=IngestionSourceType.COMBINED,
            errors=(
                IngestionError(
                    source_type=IngestionSourceType.RUN_HISTORY,
                    code="malformed_jsonl",
                    message="JSONL line could not be decoded.",
                ),
            ),
        )
    )

    assert summary.overall_status is SummarySeverity.ERROR


def test_recommended_actions_from_deterministic_signals() -> None:
    """Build deterministic recommendations from local signals only."""
    summary = build_agentops_summary(
        IngestionResult(
            source_type=IngestionSourceType.COMBINED,
            records=(
                _workflow_run("run-failed", status=WorkflowStatus.FAILED),
                _approval("approval-pending", status=ApprovalStatus.PENDING),
                GuardrailEvidenceRecord(
                    path=Path("guardrail.txt"),
                    status=GuardrailStatus.FAILED,
                    matched_signals=("failed",),
                    line_count=1,
                ),
            ),
        )
    )

    assert summary.recommended_actions == (
        "Review failed or blocked guardrail output before continuing.",
        "Inspect failed workflow run records.",
        "Review pending approvals and human-review report findings.",
    )


def test_control_tower_view_from_existing_ingestion_result() -> None:
    """Build a combined view from an existing ingestion result."""
    result = IngestionResult(
        source_type=IngestionSourceType.COMBINED,
        records=(_workflow_run("run-ok"),),
    )

    view = build_agentops_control_tower_view(ingestion_result=result)

    assert view.ingestion_result is result
    assert view.summary.workflow_runs.total == 1
    assert view.timeline.event_count == 1


def test_control_tower_view_from_temporary_local_sources(tmp_path: Path) -> None:
    """Build a combined view from temporary local source files."""
    run_history = tmp_path / "workflow-runs.jsonl"
    approvals = tmp_path / "approval-requests.jsonl"
    report = tmp_path / "report.md"
    guardrail = tmp_path / "guardrail.txt"
    _write_jsonl(run_history, [_run_payload("run-001")])
    _write_jsonl(approvals, [_approval_payload("approval-001")])
    report.write_text(_report_text(), encoding="utf-8")
    guardrail.write_text("guardrail checks passed clean\n", encoding="utf-8")

    view = build_agentops_control_tower_view(
        run_history_path=run_history,
        approval_requests_path=approvals,
        markdown_report_path=report,
        guardrail_output_text_path=guardrail,
    )

    assert view.ingestion_result.ok
    assert view.summary.workflow_runs.total == 1
    assert view.timeline.event_count == 4


def test_no_external_or_llm_dependency_is_introduced() -> None:
    """Verify summary and timeline modules expose deterministic local APIs only."""
    import agentops_control_tower.summaries as summaries
    import agentops_control_tower.timeline as timeline

    assert "requests" not in summaries.__dict__
    assert "openai" not in summaries.__dict__
    assert "requests" not in timeline.__dict__
    assert "openai" not in timeline.__dict__


def _event_key(event: AgentOpsTimelineEvent) -> tuple[TimelineEventType, str]:
    """Return a compact event key for assertions.

    Args:
        event: Timeline event.

    Returns:
        Event type and path basename/identifier.
    """
    return (event.event_type, Path(event.identifier).name)


def _workflow_run(
    run_id: str,
    *,
    status: WorkflowStatus = WorkflowStatus.SUCCEEDED,
    started_at: datetime | None = REFERENCE_TIME,
    human_review_required: bool = False,
) -> WorkflowRunRecord:
    """Build a workflow run record for tests.

    Args:
        run_id: Workflow run identifier.
        status: Workflow status.
        started_at: Optional run start timestamp.
        human_review_required: Whether the run requires human review.

    Returns:
        Workflow run record.
    """
    return WorkflowRunRecord(
        run_id=run_id,
        workflow_name="daily_marketing_report",
        status=status,
        started_at=started_at,
        human_review_required=human_review_required,
        task_error_count=0,
    )


def _approval(
    approval_id: str,
    *,
    status: ApprovalStatus = ApprovalStatus.PENDING,
    created_at: datetime | None = REFERENCE_TIME,
) -> ApprovalRequestRecord:
    """Build an approval request record for tests.

    Args:
        approval_id: Approval request identifier.
        status: Approval status.
        created_at: Optional creation timestamp.

    Returns:
        Approval request record.
    """
    return ApprovalRequestRecord(
        approval_id=approval_id,
        status=status,
        title=f"Approval {approval_id}",
        created_at=created_at,
    )


def _report(path: Path, *, human_review_count: int = 0) -> ReportSummaryRecord:
    """Build a report summary record for tests.

    Args:
        path: Report path.
        human_review_count: Campaigns requiring human review.

    Returns:
        Report summary record.
    """
    return ReportSummaryRecord(
        path=path,
        generated_timestamp=REFERENCE_TIME,
        campaigns_processed=2,
        critical_findings=0,
        warning_findings=1,
        campaigns_requiring_human_review=human_review_count,
        required_sections={"Executive Summary": True},
    )


def _write_jsonl(path: Path, payloads: list[dict[str, object]]) -> None:
    """Write JSONL test data.

    Args:
        path: Destination file path.
        payloads: Payload objects to serialize.
    """
    path.write_text(
        "\n".join(json.dumps(payload, sort_keys=True) for payload in payloads) + "\n",
        encoding="utf-8",
    )


def _run_payload(run_id: str) -> dict[str, object]:
    """Build a sample run-history payload.

    Args:
        run_id: Workflow run identifier.

    Returns:
        Sample run-history payload.
    """
    return {
        "run_id": run_id,
        "workflow_name": "daily_marketing_report",
        "status": "succeeded",
        "started_at": "2026-05-28T12:00:00+00:00",
        "human_review_required": False,
        "task_error_count": 0,
    }


def _approval_payload(approval_id: str) -> dict[str, object]:
    """Build a sample approval request payload.

    Args:
        approval_id: Approval request identifier.

    Returns:
        Sample approval request payload.
    """
    return {
        "approval_id": approval_id,
        "status": "pending",
        "title": "Review campaign",
        "created_at": "2026-05-28T12:00:00+00:00",
    }


def _report_text() -> str:
    """Return a representative deterministic Markdown report.

    Returns:
        Markdown report text.
    """
    return """# Daily Marketing Operations Report

Generated timestamp: 2026-05-28T12:00:00+00:00

## Executive Summary
- Campaigns processed: 1.
- Critical findings: 0.
- Warning findings: 1.
- Campaigns requiring human review: 0.

## Campaign Health Overview
## Critical Anomalies
## Warning Anomalies
## Data Quality Issues
## Human Review Required
## Campaign Snapshot Table
## Deterministic Recommended Actions
## Limitations
"""
