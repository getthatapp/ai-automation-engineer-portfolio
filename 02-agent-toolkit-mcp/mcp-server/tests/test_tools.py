"""Tests for deterministic local MCP tool behavior."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from agent_toolkit_mcp.tools import (
    REQUIRED_REPORT_SECTIONS,
    check_runtime_clean,
    generate_demo_brief,
    list_pending_approvals,
    read_run_history,
    validate_report,
)


def test_validate_report_accepts_all_required_sections(tmp_path: Path) -> None:
    """Validate reports that contain every required section."""

    report_path = tmp_path / "daily-marketing-report.md"
    report_path.write_text(_build_report(REQUIRED_REPORT_SECTIONS), encoding="utf-8")

    result = validate_report(report_path)

    assert result.valid is True
    assert result.file_exists is True
    assert result.missing_sections == []
    assert result.warnings == ["Generated timestamp is missing."]


def test_validate_report_extracts_summary_values(tmp_path: Path) -> None:
    """Extract explicit report summary values without inference."""

    report_path = tmp_path / "daily-marketing-report.md"
    report_path.write_text(_build_report_with_summary(REQUIRED_REPORT_SECTIONS), encoding="utf-8")

    result = validate_report(report_path)

    assert result.valid is True
    assert result.summary.generated_timestamp == "2026-06-02T11:16:10+00:00"
    assert result.summary.campaigns_processed == 3
    assert result.summary.critical_findings == 2
    assert result.summary.warning_findings == 1
    assert result.summary.campaigns_requiring_human_review == 1
    assert result.warnings == []


def test_validate_report_reports_missing_sections(tmp_path: Path) -> None:
    """Report missing required sections from a Markdown report."""

    report_path = tmp_path / "daily-marketing-report.md"
    report_path.write_text(
        _build_report(["Executive Summary", "Campaign Health Overview"]),
        encoding="utf-8",
    )

    result = validate_report(report_path)

    assert result.valid is False
    assert "Critical Anomalies" in result.missing_sections
    assert "Limitations / Missing Data" in result.missing_sections


def test_validate_report_handles_missing_path(tmp_path: Path) -> None:
    """Return a structured invalid result for a missing report path."""

    result = validate_report(tmp_path / "missing.md")

    assert result.valid is False
    assert result.file_exists is False
    assert result.missing_sections == REQUIRED_REPORT_SECTIONS
    assert result.errors


def test_validate_report_reports_duplicate_required_section(tmp_path: Path) -> None:
    """Warn when a required report section heading is duplicated."""

    report_path = tmp_path / "daily-marketing-report.md"
    report_path.write_text(
        _build_report_with_summary(["Executive Summary", "Executive Summary"]),
        encoding="utf-8",
    )

    result = validate_report(report_path)

    assert "Duplicate required section heading: Executive Summary." in result.warnings


def test_validate_report_warns_for_empty_report(tmp_path: Path) -> None:
    """Warn clearly for empty report files."""

    report_path = tmp_path / "daily-marketing-report.md"
    report_path.write_text("", encoding="utf-8")

    result = validate_report(report_path)

    assert result.valid is False
    assert "Report is empty." in result.warnings
    assert "Generated timestamp is missing." in result.warnings


def test_validate_report_rejects_wrong_suffix(tmp_path: Path) -> None:
    """Reject non-Markdown report paths with structured errors."""

    report_path = tmp_path / "daily-marketing-report.txt"
    report_path.write_text("# Report\n", encoding="utf-8")

    result = validate_report(report_path)

    assert result.valid is False
    assert result.file_exists is True
    assert result.errors


def test_read_run_history_returns_recent_records(tmp_path: Path) -> None:
    """Read recent workflow records up to the provided limit."""

    history_path = tmp_path / "workflow-runs.jsonl"
    _write_jsonl(
        history_path,
        [
            {"run_id": "run-1", "status": "success"},
            {"run_id": "run-2", "status": "needs_approval"},
            {"run_id": "run-3", "status": "failed"},
        ],
    )

    result = read_run_history(history_path, limit=2)

    assert result.file_exists is True
    assert [record["run_id"] for record in result.records] == ["run-2", "run-3"]
    assert result.total_records_read == 3
    assert result.malformed_lines == []


def test_read_run_history_reports_invalid_limits(tmp_path: Path) -> None:
    """Return structured errors for out-of-range limits."""

    history_path = tmp_path / "workflow-runs.jsonl"
    _write_jsonl(history_path, [{"run_id": "run-1"}])

    zero_result = read_run_history(history_path, limit=0)
    large_result = read_run_history(history_path, limit=101)

    assert zero_result.records == []
    assert zero_result.errors
    assert large_result.records == []
    assert large_result.errors


def test_read_run_history_handles_missing_file(tmp_path: Path) -> None:
    """Return an empty safe result when run history JSONL is missing."""

    result = read_run_history(tmp_path / "workflow-runs.jsonl")

    assert result.file_exists is False
    assert result.records == []
    assert result.total_records_read == 0
    assert result.malformed_lines == []


def test_read_run_history_rejects_directory_path(tmp_path: Path) -> None:
    """Return a structured error when JSONL path is a directory."""

    result = read_run_history(tmp_path)

    assert result.file_exists is True
    assert result.records == []
    assert result.errors


def test_read_run_history_reports_malformed_line(tmp_path: Path) -> None:
    """Report malformed JSONL lines explicitly while preserving valid records."""

    history_path = tmp_path / "workflow-runs.jsonl"
    history_path.write_text(
        '{"run_id": "run-1", "status": "success"}\n'
        '{"run_id": "broken"\n'
        '["not", "an", "object"]\n',
        encoding="utf-8",
    )

    result = read_run_history(history_path)

    assert [record["run_id"] for record in result.records] == ["run-1"]
    assert [error.line_number for error in result.malformed_lines] == [2, 3]


def test_list_pending_approvals_returns_summaries(tmp_path: Path) -> None:
    """List only pending approvals with safe summary fields."""

    approvals_path = tmp_path / "approval-requests.jsonl"
    _write_jsonl(
        approvals_path,
        [
            {
                "approval_id": "approval-1",
                "run_id": "run-1",
                "campaign_id": "cmp-1",
                "source": "deterministic_finding",
                "source_reference": "requires_human_review",
                "risk_level": "high",
                "status": "pending",
                "title": "Approve follow-up",
                "created_at": "2026-06-02T00:00:00Z",
                "source_evidence": {"api_key": "should-not-return"},
            },
            {
                "approval_id": "approval-2",
                "run_id": "run-1",
                "status": "approved",
            },
        ],
    )

    result = list_pending_approvals(approvals_path)

    assert result.file_exists is True
    assert len(result.pending_approvals) == 1
    assert result.total_records_read == 2
    assert result.pending_count == 1
    assert result.pending_approvals[0].approval_id == "approval-1"
    assert not hasattr(result.pending_approvals[0], "source_evidence")


def test_list_pending_approvals_filters_mixed_statuses(tmp_path: Path) -> None:
    """Return only pending approval summaries from mixed status records."""

    approvals_path = tmp_path / "approval-requests.jsonl"
    _write_jsonl(
        approvals_path,
        [
            {"approval_id": "approval-1", "status": "pending"},
            {"approval_id": "approval-2", "status": "approved"},
            {"approval_id": "approval-3", "status": "rejected"},
            {"approval_id": "approval-4", "status": "pending", "title": "Bearer token123"},
        ],
    )

    result = list_pending_approvals(approvals_path)

    assert [approval.approval_id for approval in result.pending_approvals] == [
        "approval-1",
        "approval-4",
    ]
    assert result.pending_count == 2
    assert result.total_records_read == 4
    assert result.pending_approvals[1].title == "[REDACTED]"


def test_list_pending_approvals_handles_missing_file(tmp_path: Path) -> None:
    """Return an empty safe result when approval JSONL is missing."""

    result = list_pending_approvals(tmp_path / "approval-requests.jsonl")

    assert result.file_exists is False
    assert result.pending_approvals == []
    assert result.pending_count == 0
    assert result.malformed_lines == []


def test_check_runtime_clean_true(tmp_path: Path) -> None:
    """Report a clean runtime state when generated artifacts are absent."""

    project_path = tmp_path / "project-1"
    project_path.mkdir()

    result = check_runtime_clean(project_path)

    assert result.clean is True
    assert result.found_paths == []


def test_check_runtime_clean_false_with_generated_files(tmp_path: Path) -> None:
    """Report generated runtime files without deleting them."""

    project_path = tmp_path / "project-1"
    (project_path / "reports").mkdir(parents=True)
    (project_path / "run-history").mkdir()
    (project_path / "approval-requests").mkdir()
    (project_path / "src" / "__pycache__").mkdir(parents=True)
    (project_path / "reports" / "daily-marketing-report-20260602T000000Z.md").write_text(
        "# Report\n",
        encoding="utf-8",
    )
    (project_path / "run-history" / "workflow-runs.jsonl").write_text("", encoding="utf-8")
    (project_path / "approval-requests" / "approval-requests.jsonl").write_text(
        "",
        encoding="utf-8",
    )
    (project_path / "src" / "__pycache__" / "module.pyc").write_bytes(b"pyc")

    result = check_runtime_clean(project_path)

    assert result.clean is False
    assert result.found_paths == [
        "approval-requests/approval-requests.jsonl",
        "reports/daily-marketing-report-20260602T000000Z.md",
        "run-history/workflow-runs.jsonl",
        "src/__pycache__",
        "src/__pycache__/module.pyc",
    ]
    assert result.artifact_counts.reports == 1
    assert result.artifact_counts.run_history == 1
    assert result.artifact_counts.approval_requests == 1
    assert result.artifact_counts.pycache == 1
    assert result.artifact_counts.pyc == 1
    assert (project_path / "run-history" / "workflow-runs.jsonl").exists()


def test_check_runtime_clean_reports_symlink_escape(tmp_path: Path) -> None:
    """Report symlink matches that resolve outside the provided project path."""

    project_path = tmp_path / "project-1"
    outside_path = tmp_path / "outside"
    (project_path / "reports").mkdir(parents=True)
    outside_path.mkdir()
    outside_report = outside_path / "daily-marketing-report-20260602T000000Z.md"
    outside_report.write_text("# Report\n", encoding="utf-8")
    symlink_path = project_path / "reports" / "daily-marketing-report-20260602T000000Z.md"
    try:
        symlink_path.symlink_to(outside_report)
    except OSError as exc:
        pytest.skip(f"Symlink creation is unavailable: {exc}")

    result = check_runtime_clean(project_path)

    assert result.clean is False
    assert result.found_paths == []
    assert result.errors


def test_generate_demo_brief_includes_expected_local_commands(tmp_path: Path) -> None:
    """Generate deterministic demo brief text with expected local commands."""

    project_path = tmp_path / "project-1"
    _create_expected_project_1_files(project_path)

    result = generate_demo_brief(project_path)

    assert result.ready is True
    assert "uv sync" in result.brief
    assert "./scripts/start_services.sh" in result.brief
    assert "NOTIFICATION_DELIVERY_ENABLED=true ./scripts/run_workflow.sh" in result.local_commands
    assert all(check.ready for check in result.readiness_checklist)


def test_generate_demo_brief_reports_missing_readiness_items(tmp_path: Path) -> None:
    """Return missing files and checklist items for incomplete projects."""

    project_path = tmp_path / "project-1"
    project_path.mkdir()

    result = generate_demo_brief(project_path)

    assert result.ready is False
    assert "README.md" in result.missing_paths
    assert any(not check.ready for check in result.readiness_checklist)


def test_secret_like_values_are_redacted_from_outputs(tmp_path: Path) -> None:
    """Redact secret-like keys and values from JSONL tool outputs."""

    history_path = tmp_path / "workflow-runs.jsonl"
    _write_jsonl(
        history_path,
        [
            {
                "run_id": "run-1",
                "password": "local-password",
                "nested": {"api_key": "sk-test-secret"},
                "message": "Bearer abc123",
            }
        ],
    )
    approvals_path = tmp_path / "approval-requests.jsonl"
    _write_jsonl(
        approvals_path,
        [
            {
                "approval_id": "approval-1",
                "status": "pending",
                "title": "Bearer abc123",
                "source_reference": "requires_human_review",
            }
        ],
    )

    history_result = read_run_history(history_path)
    approvals_result = list_pending_approvals(approvals_path)

    assert history_result.records[0]["password"] == "[REDACTED]"
    assert history_result.records[0]["nested"]["api_key"] == "[REDACTED]"
    assert history_result.records[0]["message"] == "[REDACTED]"
    assert approvals_result.pending_approvals[0].title == "[REDACTED]"


def _build_report(sections: list[str]) -> str:
    """Build a Markdown report fixture from section headings.

    Args:
        sections: Section headings to include.

    Returns:
        Markdown report text.
    """

    section_text = "\n\n".join(f"## {section}\nContent." for section in sections)
    return f"# Daily Marketing Operations Report\n\n{section_text}\n"


def _build_report_with_summary(sections: list[str]) -> str:
    """Build a Markdown report fixture with explicit summary lines.

    Args:
        sections: Section headings to include.

    Returns:
        Markdown report text with extractable summary values.
    """

    summary = "\n".join(
        [
            "Generated timestamp: 2026-06-02T11:16:10+00:00",
            "",
            "- Campaigns processed: 3.",
            "- Critical findings: 2.",
            "- Warning findings: 1.",
            "- Campaigns requiring human review: 1.",
        ]
    )
    section_text = "\n\n".join(f"## {section}\nContent." for section in sections)
    return f"# Daily Marketing Operations Report\n\n{summary}\n\n{section_text}\n"


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    """Write JSONL fixture records.

    Args:
        path: Destination JSONL path.
        records: JSON object records to write.
    """

    path.write_text(
        "".join(f"{json.dumps(record)}\n" for record in records),
        encoding="utf-8",
    )


def _create_expected_project_1_files(project_path: Path) -> None:
    """Create the expected Project 1 file layout for demo brief tests.

    Args:
        project_path: Temporary project path to populate.
    """

    expected_paths = [
        "README.md",
        "AGENTS.md",
        "pyproject.toml",
        "compose.yaml",
        "docs/ARCHITECTURE.md",
        "docs/RUNBOOK.md",
        "scripts/start_services.sh",
        "scripts/run_workflow.sh",
        "scripts/run_workflow_with_llm.sh",
        "scripts/run_checks.sh",
        "src/marketing_ops_agent/workflows/daily_marketing_report.py",
    ]
    for relative_path in expected_paths:
        file_path = project_path / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text("placeholder\n", encoding="utf-8")
    for directory in ("reports", "run-history", "approval-requests"):
        (project_path / directory).mkdir(parents=True, exist_ok=True)
    ci_workflow_path = project_path.parent / ".github" / "workflows" / "project-1-ci.yml"
    ci_workflow_path.parent.mkdir(parents=True, exist_ok=True)
    ci_workflow_path.write_text("placeholder\n", encoding="utf-8")
