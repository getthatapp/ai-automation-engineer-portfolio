"""Tests for deterministic static AgentOps HTML reporting."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from agentops_control_tower.html_reporting import render_agentops_html_report
from agentops_control_tower.models import (
    AgentOpsControlTowerView,
    ApprovalRequestRecord,
    ApprovalStatus,
    GuardrailEvidenceRecord,
    GuardrailStatus,
    IngestionError,
    IngestionResult,
    IngestionSourceType,
    IngestionWarning,
    ReportSummaryRecord,
    ToolEvidenceRecord,
    WorkflowRunRecord,
    WorkflowStatus,
)
from agentops_control_tower.summaries import build_agentops_control_tower_view

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REFERENCE_TIME = datetime(2026, 5, 28, 12, 0, tzinfo=UTC)


def test_html_report_contains_expected_sections() -> None:
    """Render all required static HTML report sections."""
    html = render_agentops_html_report(_view_with_records())

    assert html.startswith("<!doctype html>")
    expected_sections = [
        "Input Source Paths",
        "Overall Health Status",
        "Workflow Summary",
        "Approval Summary",
        "Report Health Summary",
        "Tool Evidence Summary",
        "Guardrail Summary",
        "Ingestion Warnings",
        "Ingestion Errors",
        "Timeline",
        "Deterministic Recommended Actions",
        "Limitations / Missing Data",
    ]
    for section in expected_sections:
        assert f"<h2>{section}</h2>" in html


def test_html_report_escapes_dynamic_text() -> None:
    """Escape dynamic source values before inserting them into HTML."""
    view = build_agentops_control_tower_view(
        ingestion_result=IngestionResult(
            source_type=IngestionSourceType.COMBINED,
            records=(
                WorkflowRunRecord(
                    run_id="run-<script>",
                    workflow_name="daily_marketing_report",
                    status=WorkflowStatus.FAILED,
                    started_at=REFERENCE_TIME,
                    failure_message="<secret>",
                ),
            ),
            warnings=(
                IngestionWarning(
                    source_type=IngestionSourceType.MARKDOWN_REPORT,
                    path=Path("report-<unsafe>.md"),
                    code="missing_report_section",
                    message="Missing <section> & details.",
                ),
            ),
            errors=(
                IngestionError(
                    source_type=IngestionSourceType.RUN_HISTORY,
                    path=Path("workflow-<runs>.jsonl"),
                    code="malformed_jsonl",
                    message="Bad <json> & input.",
                    line_number=1,
                ),
            ),
        )
    )

    html = render_agentops_html_report(view)

    assert "run-&lt;script&gt;" in html
    assert "report-&lt;unsafe&gt;.md" in html
    assert "Missing &lt;section&gt; &amp; details." in html
    assert "workflow-&lt;runs&gt;.jsonl" in html
    assert "Bad &lt;json&gt; &amp; input." in html
    assert "run-<script>" not in html


def test_html_report_has_no_external_assets_or_scripts() -> None:
    """Keep static HTML self-contained with no external frontend assets."""
    html = render_agentops_html_report(_view_with_records()).lower()

    forbidden = (
        "<script",
        'rel="stylesheet"',
        "http://",
        "https://",
        "cdn.",
        "<img",
        "@import",
    )
    assert not any(token in html for token in forbidden)


def test_html_report_rendering_is_stable() -> None:
    """Render identical HTML for identical typed views."""
    view = _view_with_records()

    first = render_agentops_html_report(view)
    second = render_agentops_html_report(view)

    assert first == second


def test_html_report_uses_source_timestamp_without_wall_clock() -> None:
    """Use parsed source report timestamp for deterministic timestamp display."""
    html = render_agentops_html_report(_view_with_records())

    assert "Generated timestamp / source timestamp: 2026-05-28T12:00:00+00:00" in html


def test_html_report_shows_unavailable_timestamp_when_missing() -> None:
    """Render `Unavailable` when no source report timestamp exists."""
    view = build_agentops_control_tower_view(
        ingestion_result=IngestionResult(source_type=IngestionSourceType.COMBINED)
    )

    html = render_agentops_html_report(view)

    assert "Generated timestamp / source timestamp: Unavailable" in html


def test_html_report_uses_project_relative_source_paths() -> None:
    """Render project-local source paths relative to the Project 3 root."""
    report_path = PROJECT_ROOT / "exports/reviewer-demo/input/daily-marketing-report-review.md"
    tool_path = PROJECT_ROOT / "exports/reviewer-demo/input/tool-evidence-not-ready.json"
    guardrail_path = PROJECT_ROOT / "exports/reviewer-demo/input/guardrail-blocked.txt"
    view = build_agentops_control_tower_view(
        ingestion_result=IngestionResult(
            source_type=IngestionSourceType.COMBINED,
            records=(
                ReportSummaryRecord(path=report_path, generated_timestamp=REFERENCE_TIME),
                ToolEvidenceRecord(path=tool_path, tool_name="generate_demo_brief", ready=False),
                GuardrailEvidenceRecord(
                    path=guardrail_path,
                    status=GuardrailStatus.BLOCKED,
                    matched_signals=("blocked",),
                    line_count=1,
                ),
            ),
        )
    ).model_copy(
        update={
            "input_paths": {
                IngestionSourceType.RUN_HISTORY: PROJECT_ROOT
                / "exports/reviewer-demo/input/workflow-runs.jsonl",
                IngestionSourceType.APPROVAL_REQUESTS: PROJECT_ROOT
                / "exports/reviewer-demo/input/approval-requests.jsonl",
            }
        }
    )

    html = render_agentops_html_report(view)

    assert str(PROJECT_ROOT) not in html
    assert "exports/reviewer-demo/input/workflow-runs.jsonl" in html
    assert "exports/reviewer-demo/input/approval-requests.jsonl" in html
    assert "exports/reviewer-demo/input/daily-marketing-report-review.md" in html
    assert "exports/reviewer-demo/input/tool-evidence-not-ready.json" in html
    assert "exports/reviewer-demo/input/guardrail-blocked.txt" in html


def test_html_report_keeps_outside_project_paths_readable() -> None:
    """Render paths outside the project root without raising errors."""
    outside_path = Path("/tmp/outside-agentops-report.md")
    view = build_agentops_control_tower_view(
        ingestion_result=IngestionResult(
            source_type=IngestionSourceType.COMBINED,
            records=(ReportSummaryRecord(path=outside_path),),
        )
    )

    html = render_agentops_html_report(view)

    assert "/tmp/outside-agentops-report.md" in html


def _view_with_records() -> AgentOpsControlTowerView:
    """Build a deterministic view with representative records.

    Returns:
        Combined local AgentOps control tower view.
    """
    return build_agentops_control_tower_view(
        ingestion_result=IngestionResult(
            source_type=IngestionSourceType.COMBINED,
            records=(
                WorkflowRunRecord(
                    run_id="run-001",
                    workflow_name="daily_marketing_report",
                    status=WorkflowStatus.SUCCEEDED,
                    started_at=REFERENCE_TIME,
                ),
                ApprovalRequestRecord(
                    approval_id="approval-001",
                    status=ApprovalStatus.PENDING,
                    title="Review campaign",
                    created_at=REFERENCE_TIME,
                ),
                ReportSummaryRecord(
                    path=Path("report.md"),
                    generated_timestamp=REFERENCE_TIME,
                    campaigns_processed=2,
                    critical_findings=0,
                    warning_findings=1,
                    campaigns_requiring_human_review=1,
                    required_sections={"Executive Summary": True},
                ),
                ToolEvidenceRecord(
                    path=Path("tool-evidence.json"),
                    tool_name="check_runtime_clean",
                    status="ok",
                    ready=True,
                ),
                GuardrailEvidenceRecord(
                    path=Path("guardrail.txt"),
                    status=GuardrailStatus.PASSED,
                    matched_signals=("passed",),
                    line_count=1,
                ),
            ),
        )
    )
