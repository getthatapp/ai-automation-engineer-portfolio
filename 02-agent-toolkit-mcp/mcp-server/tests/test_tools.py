"""Tests for deterministic local MCP tool behavior."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

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
    assert result.malformed_lines == []


def test_read_run_history_handles_missing_file(tmp_path: Path) -> None:
    """Return an empty safe result when run history JSONL is missing."""

    result = read_run_history(tmp_path / "workflow-runs.jsonl")

    assert result.file_exists is False
    assert result.records == []
    assert result.malformed_lines == []


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
    assert result.pending_approvals[0].approval_id == "approval-1"
    assert not hasattr(result.pending_approvals[0], "source_evidence")


def test_list_pending_approvals_handles_missing_file(tmp_path: Path) -> None:
    """Return an empty safe result when approval JSONL is missing."""

    result = list_pending_approvals(tmp_path / "approval-requests.jsonl")

    assert result.file_exists is False
    assert result.pending_approvals == []
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
    assert (project_path / "run-history" / "workflow-runs.jsonl").exists()


def test_generate_demo_brief_includes_expected_local_commands(tmp_path: Path) -> None:
    """Generate deterministic demo brief text with expected local commands."""

    project_path = tmp_path / "project-1"
    _create_expected_project_1_files(project_path)

    result = generate_demo_brief(project_path)

    assert result.ready is True
    assert "uv sync" in result.brief
    assert "./scripts/start_services.sh" in result.brief
    assert "NOTIFICATION_DELIVERY_ENABLED=true ./scripts/run_workflow.sh" in result.local_commands


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
