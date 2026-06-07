"""Tests for deterministic AgentOps Markdown reporting."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from agentops_control_tower.models import (
    ApprovalRequestRecord,
    ApprovalStatus,
    GuardrailEvidenceRecord,
    GuardrailStatus,
    IngestionResult,
    IngestionSourceType,
    ReportSummaryRecord,
    WorkflowRunRecord,
    WorkflowStatus,
)
from agentops_control_tower.reporting import render_agentops_markdown_report
from agentops_control_tower.summaries import build_agentops_control_tower_view

REFERENCE_TIME = datetime(2026, 5, 28, 12, 0, tzinfo=UTC)


def test_report_includes_deterministic_recommended_actions() -> None:
    """Render deterministic recommended actions from summary signals."""
    view = build_agentops_control_tower_view(
        ingestion_result=IngestionResult(
            source_type=IngestionSourceType.COMBINED,
            records=(
                WorkflowRunRecord(
                    run_id="run-failed",
                    workflow_name="daily_marketing_report",
                    status=WorkflowStatus.FAILED,
                    started_at=REFERENCE_TIME,
                    human_review_required=True,
                ),
                ApprovalRequestRecord(
                    approval_id="approval-pending",
                    status=ApprovalStatus.PENDING,
                    created_at=REFERENCE_TIME,
                ),
            ),
        )
    )

    report = render_agentops_markdown_report(view)

    assert "## Deterministic Recommended Actions" in report
    assert "- Inspect failed workflow run records." in report
    assert "- Review pending approvals and human-review report findings." in report


def test_report_includes_limitations_and_missing_data() -> None:
    """Render clear limitations and missing-data lines."""
    view = build_agentops_control_tower_view(
        ingestion_result=IngestionResult(source_type=IngestionSourceType.COMBINED)
    )

    report = render_agentops_markdown_report(view)

    assert "## Limitations / Missing Data" in report
    assert "- No dashboard/UI is implemented in this local milestone." in report
    assert "- No workflow run-history records were available." in report
    assert "- No saved Project 2 tool evidence was available." in report


def test_render_agentops_markdown_report_deterministic_ordering() -> None:
    """Render identical report text for identical typed views."""
    view = build_agentops_control_tower_view(
        ingestion_result=IngestionResult(
            source_type=IngestionSourceType.COMBINED,
            records=(
                GuardrailEvidenceRecord(
                    path=Path("guardrail.txt"),
                    status=GuardrailStatus.PASSED,
                    matched_signals=("passed",),
                    line_count=1,
                ),
                ReportSummaryRecord(
                    path=Path("report.md"),
                    generated_timestamp=REFERENCE_TIME,
                    campaigns_processed=2,
                    critical_findings=0,
                    warning_findings=1,
                    campaigns_requiring_human_review=0,
                    required_sections={"Executive Summary": True},
                ),
            ),
        )
    )

    first = render_agentops_markdown_report(view)
    second = render_agentops_markdown_report(view)

    assert first == second
    assert first.index("## Input Source Paths") < first.index("## Overall Health Status")
    assert first.index("## Timeline") < first.index("## Deterministic Recommended Actions")


def test_report_uses_source_timestamp_without_wall_clock() -> None:
    """Use parsed source report timestamp for deterministic generated timestamp."""
    view = build_agentops_control_tower_view(
        ingestion_result=IngestionResult(
            source_type=IngestionSourceType.COMBINED,
            records=(
                ReportSummaryRecord(
                    path=Path("report.md"),
                    generated_timestamp=REFERENCE_TIME,
                    required_sections={"Executive Summary": True},
                ),
            ),
        )
    )

    report = render_agentops_markdown_report(view)

    assert "Generated timestamp: 2026-05-28T12:00:00+00:00" in report
