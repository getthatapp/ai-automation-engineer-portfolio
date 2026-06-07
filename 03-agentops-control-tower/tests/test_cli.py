"""Tests for the local AgentOps control tower CLI."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentops_control_tower.cli import EXIT_INGESTION_ERROR, EXIT_SUCCESS, EXIT_USAGE_ERROR, main
from agentops_control_tower.models import (
    GuardrailEvidenceRecord,
    GuardrailStatus,
    IngestionResult,
    IngestionSourceType,
    ReportSummaryRecord,
    ToolEvidenceRecord,
)
from agentops_control_tower.summaries import build_agentops_control_tower_view

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_cli_help_lists_commands(capsys: pytest.CaptureFixture[str]) -> None:
    """Show the top-level CLI help with available commands."""
    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])

    assert exc_info.value.code == 0
    output = capsys.readouterr().out
    assert "summary" in output
    assert "timeline" in output
    assert "export-report" in output


def test_summary_json_output(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Print compact summary JSON by default."""
    sources = _write_sources(tmp_path)

    exit_code = main(["summary", *sources.args])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == EXIT_SUCCESS
    assert payload["overall_status"] == "needs_attention"
    assert payload["workflow_runs"]["total"] == 1
    assert payload["approvals"]["pending_count"] == 1
    assert "\n  " not in captured.out


def test_summary_pretty_output(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Print indented summary JSON when requested."""
    sources = _write_sources(tmp_path)

    exit_code = main(["summary", "--pretty", *sources.args])

    captured = capsys.readouterr()
    assert exit_code == EXIT_SUCCESS
    assert json.loads(captured.out)["reports"]["total"] == 1
    assert "\n  " in captured.out


def test_timeline_json_output(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Print compact timeline JSON by default."""
    sources = _write_sources(tmp_path)

    exit_code = main(["timeline", *sources.args])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == EXIT_SUCCESS
    assert len(payload["events"]) == 5
    assert payload["events"][0]["event_type"] == "workflow_run"


def test_timeline_json_uses_project_relative_file_identifiers(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Print project-relative identifiers for Project 3 file-backed events."""
    report_path = PROJECT_ROOT / "exports/reviewer-demo/input/daily-marketing-report-review.md"
    tool_path = PROJECT_ROOT / "exports/reviewer-demo/input/tool-evidence-not-ready.json"
    guardrail_path = PROJECT_ROOT / "exports/reviewer-demo/input/guardrail-blocked.txt"
    view = build_agentops_control_tower_view(
        ingestion_result=IngestionResult(
            source_type=IngestionSourceType.COMBINED,
            records=(
                ReportSummaryRecord(path=report_path),
                ToolEvidenceRecord(path=tool_path, tool_name="check_demo_readiness", ready=False),
                GuardrailEvidenceRecord(
                    path=guardrail_path,
                    status=GuardrailStatus.BLOCKED,
                    matched_signals=("blocked",),
                    line_count=1,
                ),
            ),
        )
    )

    monkeypatch.setattr("agentops_control_tower.cli._build_view_from_args", lambda _args: view)

    exit_code = main(["timeline", "--pretty"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    identifiers = [event["identifier"] for event in payload["events"]]
    assert exit_code == EXIT_SUCCESS
    assert str(PROJECT_ROOT) not in captured.out
    assert "exports/reviewer-demo/input/daily-marketing-report-review.md" in identifiers
    assert "exports/reviewer-demo/input/tool-evidence-not-ready.json" in identifiers
    assert "exports/reviewer-demo/input/guardrail-blocked.txt" in identifiers
    assert [event["event_type"] for event in payload["events"]] == [
        "report_summary",
        "tool_evidence",
        "guardrail_evidence",
    ]


def test_export_report_stdout_markdown(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Print deterministic Markdown report to stdout by default."""
    sources = _write_sources(tmp_path)

    exit_code = main(["export-report", *sources.args])

    output = capsys.readouterr().out
    assert exit_code == EXIT_SUCCESS
    assert output.startswith("# AgentOps Control Tower Report")
    assert "## Timeline" in output
    assert "## Limitations / Missing Data" in output
    assert "workflow-runs.jsonl" in output
    assert "approval-requests.jsonl" in output


def test_export_report_output_writes_file(tmp_path: Path) -> None:
    """Write deterministic Markdown report to a requested output path."""
    sources = _write_sources(tmp_path)
    output = tmp_path / "nested" / "report.md"

    exit_code = main(["export-report", *sources.args, "--output", str(output)])

    assert exit_code == EXIT_SUCCESS
    assert output.read_text(encoding="utf-8").startswith("# AgentOps Control Tower Report")


def test_export_report_html_stdout(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Print deterministic HTML report to stdout when requested."""
    sources = _write_sources(tmp_path)

    exit_code = main(["export-report", "--format", "html", *sources.args])

    output = capsys.readouterr().out
    assert exit_code == EXIT_SUCCESS
    assert output.startswith("<!doctype html>")
    assert "<h1>AgentOps Control Tower Report</h1>" in output
    assert "<h2>Timeline</h2>" in output


def test_export_report_html_output_writes_file(tmp_path: Path) -> None:
    """Write deterministic HTML report to a requested output path."""
    sources = _write_sources(tmp_path)
    output = tmp_path / "nested" / "report.html"

    exit_code = main(
        ["export-report", "--format", "html", *sources.args, "--output", str(output)]
    )

    assert exit_code == EXIT_SUCCESS
    assert output.read_text(encoding="utf-8").startswith("<!doctype html>")


def test_export_report_refuses_overwrite_by_default(tmp_path: Path) -> None:
    """Return non-zero when an output file already exists."""
    sources = _write_sources(tmp_path)
    output = tmp_path / "report.md"
    output.write_text("existing\n", encoding="utf-8")

    exit_code = main(["export-report", *sources.args, "--output", str(output)])

    assert exit_code == EXIT_USAGE_ERROR
    assert output.read_text(encoding="utf-8") == "existing\n"


def test_export_report_html_refuses_overwrite_by_default(tmp_path: Path) -> None:
    """Return non-zero when an HTML output file already exists."""
    sources = _write_sources(tmp_path)
    output = tmp_path / "report.html"
    output.write_text("existing\n", encoding="utf-8")

    exit_code = main(
        ["export-report", "--format", "html", *sources.args, "--output", str(output)]
    )

    assert exit_code == EXIT_USAGE_ERROR
    assert output.read_text(encoding="utf-8") == "existing\n"


def test_export_report_overwrites_with_flag(tmp_path: Path) -> None:
    """Overwrite an existing report file when explicitly requested."""
    sources = _write_sources(tmp_path)
    output = tmp_path / "report.md"
    output.write_text("existing\n", encoding="utf-8")

    exit_code = main(["export-report", *sources.args, "--output", str(output), "--overwrite"])

    assert exit_code == EXIT_SUCCESS
    assert output.read_text(encoding="utf-8").startswith("# AgentOps Control Tower Report")


def test_export_report_html_overwrites_with_flag(tmp_path: Path) -> None:
    """Overwrite an existing HTML report file when explicitly requested."""
    sources = _write_sources(tmp_path)
    output = tmp_path / "report.html"
    output.write_text("existing\n", encoding="utf-8")

    exit_code = main(
        [
            "export-report",
            "--format",
            "html",
            *sources.args,
            "--output",
            str(output),
            "--overwrite",
        ]
    )

    assert exit_code == EXIT_SUCCESS
    assert output.read_text(encoding="utf-8").startswith("<!doctype html>")


def test_malformed_jsonl_returns_non_zero(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Return non-zero when ingestion captures malformed JSONL."""
    run_history = tmp_path / "workflow-runs.jsonl"
    run_history.write_text("{not-json\n", encoding="utf-8")

    exit_code = main(["summary", "--run-history", str(run_history)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == EXIT_INGESTION_ERROR
    assert payload["ingestion_error_count"] == 1
    assert "ingestion completed with 1 error" in captured.err


def test_warnings_do_not_force_non_zero(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Return zero when ingestion has warnings but no errors."""
    missing_report = tmp_path / "missing-report.md"

    exit_code = main(["summary", "--report", str(missing_report)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == EXIT_SUCCESS
    assert payload["ingestion_warning_count"] == 1
    assert payload["ingestion_error_count"] == 0


def test_cli_uses_no_external_api_or_llm_imports() -> None:
    """Keep CLI/reporting implementation free of external API and LLM imports."""
    cli_source = Path("src/agentops_control_tower/cli.py").read_text(encoding="utf-8")
    reporting_source = Path("src/agentops_control_tower/reporting.py").read_text(encoding="utf-8")
    html_reporting_source = Path("src/agentops_control_tower/html_reporting.py").read_text(
        encoding="utf-8"
    )
    combined = f"{cli_source}\n{reporting_source}\n{html_reporting_source}"

    forbidden = (
        "import openai",
        "import requests",
        "import httpx",
        "import urllib.request",
        "import anthropic",
        "from openai",
        "from requests",
        "from httpx",
        "from urllib.request",
        "from anthropic",
    )
    assert not any(name in combined for name in forbidden)


class _SourcePaths:
    """Temporary local source paths for CLI tests."""

    def __init__(
        self,
        *,
        run_history: Path,
        approvals: Path,
        report: Path,
        tool: Path,
        guardrail: Path,
    ) -> None:
        """Store source paths for test command arguments.

        Args:
            run_history: Workflow run-history JSONL path.
            approvals: Approval requests JSONL path.
            report: Deterministic Markdown report path.
            tool: Saved Project 2 tool evidence JSON path.
            guardrail: Saved guardrail output text path.
        """
        self.run_history = run_history
        self.approvals = approvals
        self.report = report
        self.tool = tool
        self.guardrail = guardrail

    @property
    def args(self) -> list[str]:
        """Return CLI arguments for all source paths.

        Returns:
            Source path arguments.
        """
        return [
            "--run-history",
            str(self.run_history),
            "--approval-requests",
            str(self.approvals),
            "--report",
            str(self.report),
            "--tool-evidence",
            str(self.tool),
            "--guardrail-output",
            str(self.guardrail),
        ]


def _write_sources(tmp_path: Path) -> _SourcePaths:
    """Write deterministic temporary source files.

    Args:
        tmp_path: Pytest temporary directory.

    Returns:
        Source path container.
    """
    run_history = tmp_path / "workflow-runs.jsonl"
    approvals = tmp_path / "approval-requests.jsonl"
    report = tmp_path / "daily-marketing-report.md"
    tool = tmp_path / "tool-evidence.json"
    guardrail = tmp_path / "guardrail.txt"

    run_history.write_text(
        json.dumps(
            {
                "run_id": "run-001",
                "workflow_name": "daily_marketing_report",
                "status": "succeeded",
                "started_at": "2026-05-28T12:00:00+00:00",
                "finished_at": "2026-05-28T12:00:03+00:00",
                "duration_seconds": 3.0,
                "human_review_required": False,
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    approvals.write_text(
        json.dumps(
            {
                "approval_id": "approval-001",
                "run_id": "run-001",
                "status": "pending",
                "source": "deterministic_finding",
                "title": "Review campaign",
                "created_at": "2026-05-28T12:01:00+00:00",
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    report.write_text(_report_text(), encoding="utf-8")
    tool.write_text(
        json.dumps({"tool_name": "check_runtime_clean", "status": "ok", "ready": True}),
        encoding="utf-8",
    )
    guardrail.write_text("guardrail checks passed clean\n", encoding="utf-8")
    return _SourcePaths(
        run_history=run_history,
        approvals=approvals,
        report=report,
        tool=tool,
        guardrail=guardrail,
    )


def _report_text() -> str:
    """Return deterministic Markdown report source text.

    Returns:
        Markdown report text with all required sections.
    """
    return """# Daily Marketing Operations Report

Generated timestamp: 2026-05-28T12:00:00+00:00

## Executive Summary
- Campaigns processed: 2.
- Critical findings: 0.
- Warning findings: 1.
- Campaigns requiring human review: 1.

## Campaign Health Overview
## Critical Anomalies
## Warning Anomalies
## Data Quality Issues
## Human Review Required
## Campaign Snapshot Table
## Deterministic Recommended Actions
## Limitations
"""
