"""Tests for the deterministic local MCP command-line interface."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from agent_toolkit_mcp import cli
from agent_toolkit_mcp.tools import REQUIRED_REPORT_SECTIONS


def test_validate_report_cli_prints_json_and_success_exit(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Validate a complete report and return JSON evidence with exit code zero."""

    report_path = tmp_path / "daily-marketing-report.md"
    report_path.write_text(_build_report(REQUIRED_REPORT_SECTIONS), encoding="utf-8")

    exit_code = cli.main(["validate-report", str(report_path)])
    payload = _read_stdout_json(capsys)

    assert exit_code == 0
    assert payload["valid"] is True
    assert payload["file_exists"] is True
    assert payload["missing_sections"] == []


def test_validate_report_cli_returns_nonzero_for_invalid_report(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Return nonzero while still printing JSON evidence for invalid reports."""

    report_path = tmp_path / "daily-marketing-report.md"
    report_path.write_text("## Executive Summary\nContent.\n", encoding="utf-8")

    exit_code = cli.main(["validate-report", str(report_path)])
    payload = _read_stdout_json(capsys)

    assert exit_code == 1
    assert payload["valid"] is False
    assert "Critical Anomalies" in payload["missing_sections"]


def test_validate_report_cli_pretty_prints_json(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Pretty-print indented JSON when `--pretty` is provided after a subcommand."""

    report_path = tmp_path / "daily-marketing-report.md"
    report_path.write_text(_build_report(REQUIRED_REPORT_SECTIONS), encoding="utf-8")

    exit_code = cli.main(["validate-report", str(report_path), "--pretty"])
    output = capsys.readouterr().out

    assert exit_code == 0
    assert output.startswith("{\n")
    assert '\n  "file_exists": true' in output
    assert json.loads(output)["valid"] is True


def test_read_run_history_cli_returns_recent_records(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Read recent run-history records and return exit code zero."""

    history_path = tmp_path / "workflow-runs.jsonl"
    _write_jsonl(
        history_path,
        [
            {"run_id": "run-1", "status": "success"},
            {"run_id": "run-2", "status": "failed"},
        ],
    )

    exit_code = cli.main(["read-run-history", str(history_path), "--limit", "1"])
    payload = _read_stdout_json(capsys)

    assert exit_code == 0
    assert [record["run_id"] for record in payload["records"]] == ["run-2"]
    assert payload["total_records_read"] == 2


def test_read_run_history_cli_returns_zero_for_handled_missing_file(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Treat missing run history as safe missing evidence with exit code zero."""

    exit_code = cli.main(["read-run-history", str(tmp_path / "workflow-runs.jsonl")])
    payload = _read_stdout_json(capsys)

    assert exit_code == 0
    assert payload["file_exists"] is False
    assert payload["records"] == []


def test_read_run_history_cli_returns_nonzero_for_malformed_jsonl(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Return nonzero when malformed JSONL is reported."""

    history_path = tmp_path / "workflow-runs.jsonl"
    history_path.write_text('{"run_id": "run-1"}\n{"broken"\n', encoding="utf-8")

    exit_code = cli.main(["read-run-history", str(history_path)])
    payload = _read_stdout_json(capsys)

    assert exit_code == 1
    assert [error["line_number"] for error in payload["malformed_lines"]] == [2]


def test_read_run_history_cli_returns_nonzero_for_invalid_limit(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Return nonzero when the tool reports an invalid limit."""

    history_path = tmp_path / "workflow-runs.jsonl"
    _write_jsonl(history_path, [{"run_id": "run-1"}])

    exit_code = cli.main(["read-run-history", str(history_path), "--limit", "0"])
    payload = _read_stdout_json(capsys)

    assert exit_code == 1
    assert payload["errors"]
    assert payload["records"] == []


def test_list_pending_approvals_cli_returns_summaries(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """List pending approval summaries through the CLI."""

    approvals_path = tmp_path / "approval-requests.jsonl"
    _write_jsonl(
        approvals_path,
        [
            {"approval_id": "approval-1", "status": "pending", "title": "Review"},
            {"approval_id": "approval-2", "status": "approved"},
        ],
    )

    exit_code = cli.main(["list-pending-approvals", str(approvals_path)])
    payload = _read_stdout_json(capsys)

    assert exit_code == 0
    assert payload["pending_count"] == 1
    assert payload["pending_approvals"][0]["approval_id"] == "approval-1"


def test_list_pending_approvals_cli_returns_nonzero_for_malformed_jsonl(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Return nonzero for approval queues with malformed JSONL lines."""

    approvals_path = tmp_path / "approval-requests.jsonl"
    approvals_path.write_text(
        '{"approval_id": "approval-1", "status": "pending"}\n[]\n',
        encoding="utf-8",
    )

    exit_code = cli.main(["list-pending-approvals", str(approvals_path)])
    payload = _read_stdout_json(capsys)

    assert exit_code == 1
    assert payload["malformed_lines"][0]["line_number"] == 2


def test_check_runtime_clean_cli_status_codes(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Return zero for clean runtime state and nonzero for generated artifacts."""

    project_path = tmp_path / "project-1"
    reports_path = project_path / "reports"
    reports_path.mkdir(parents=True)

    clean_exit_code = cli.main(["check-runtime-clean", str(project_path)])
    clean_payload = _read_stdout_json(capsys)

    (reports_path / "daily-marketing-report-20260602T000000Z.md").write_text(
        "# Report\n",
        encoding="utf-8",
    )
    dirty_exit_code = cli.main(["check-runtime-clean", str(project_path)])
    dirty_payload = _read_stdout_json(capsys)

    assert clean_exit_code == 0
    assert clean_payload["clean"] is True
    assert dirty_exit_code == 1
    assert dirty_payload["clean"] is False
    assert dirty_payload["artifact_counts"]["reports"] == 1


def test_generate_demo_brief_cli_status_codes(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Return zero for ready demo structure and nonzero for incomplete structure."""

    ready_project_path = tmp_path / "ready-project-1"
    incomplete_project_path = tmp_path / "incomplete-project-1"
    _create_expected_project_1_files(ready_project_path)
    incomplete_project_path.mkdir()

    ready_exit_code = cli.main(["generate-demo-brief", str(ready_project_path)])
    ready_payload = _read_stdout_json(capsys)
    incomplete_exit_code = cli.main(["generate-demo-brief", str(incomplete_project_path)])
    incomplete_payload = _read_stdout_json(capsys)

    assert ready_exit_code == 0
    assert ready_payload["ready"] is True
    assert incomplete_exit_code == 1
    assert incomplete_payload["ready"] is False
    assert "README.md" in incomplete_payload["missing_paths"]


def _read_stdout_json(capsys: pytest.CaptureFixture[str]) -> dict[str, Any]:
    """Read captured stdout as a JSON object.

    Args:
        capsys: Pytest capture fixture.

    Returns:
        Parsed JSON object.
    """

    output = capsys.readouterr().out
    payload = json.loads(output)
    assert isinstance(payload, dict)
    return payload


def _build_report(sections: list[str]) -> str:
    """Build a Markdown report fixture from section headings.

    Args:
        sections: Section headings to include.

    Returns:
        Markdown report text.
    """

    summary = "Generated timestamp: 2026-06-02T11:16:10+00:00"
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
