"""Tests for deterministic local AgentOps ingestion."""

from __future__ import annotations

import json
from pathlib import Path

from agentops_control_tower.ingestion import ingest_local_agentops_sources
from agentops_control_tower.models import (
    ApprovalRequestRecord,
    ApprovalStatus,
    GuardrailEvidenceRecord,
    GuardrailStatus,
    ReportSummaryRecord,
    ToolEvidenceRecord,
    WorkflowRunRecord,
    WorkflowStatus,
)
from agentops_control_tower.parsers import (
    parse_approval_requests_jsonl,
    parse_guardrail_output_text,
    parse_markdown_report,
    parse_run_history_jsonl,
    parse_tool_evidence_json,
)
from agentops_control_tower.sanitization import REDACTED, sanitize_value


def test_parse_run_history_jsonl_happy_path(tmp_path: Path) -> None:
    """Parse a valid Project 1 run-history JSONL file."""
    path = tmp_path / "workflow-runs.jsonl"
    _write_jsonl(
        path,
        [
            _run_payload("run-001", status="succeeded"),
            _run_payload("run-002", status="failed", failure_message="timeout"),
        ],
    )

    result = parse_run_history_jsonl(path)

    assert result.ok
    run_ids = [
        record.run_id for record in result.records if isinstance(record, WorkflowRunRecord)
    ]
    assert run_ids == [
        "run-001",
        "run-002",
    ]
    first = result.records[0]
    assert isinstance(first, WorkflowRunRecord)
    assert first.status is WorkflowStatus.SUCCEEDED
    assert first.snapshot_count == 2


def test_parse_run_history_jsonl_missing_file(tmp_path: Path) -> None:
    """Return a warning when run-history JSONL is missing."""
    result = parse_run_history_jsonl(tmp_path / "missing.jsonl")

    assert result.ok
    assert result.record_count == 0
    assert result.warnings[0].code == "missing_file"


def test_parse_run_history_jsonl_malformed_jsonl(tmp_path: Path) -> None:
    """Return an explicit error when run-history JSONL is malformed."""
    path = tmp_path / "workflow-runs.jsonl"
    path.write_text('{"run_id": "run-001"}\nnot-json\n', encoding="utf-8")

    result = parse_run_history_jsonl(path)

    assert not result.ok
    assert result.errors[0].code == "malformed_jsonl"
    assert result.errors[0].line_number == 2


def test_parse_run_history_jsonl_redacts_secrets(tmp_path: Path) -> None:
    """Redact obvious secret-like values from run-history payloads."""
    path = tmp_path / "workflow-runs.jsonl"
    payload = _run_payload(
        "run-secret",
        failure_message="request failed with token=abc123 and Bearer secret-token",
    )
    payload["api_key"] = "super-secret"
    _write_jsonl(path, [payload])

    result = parse_run_history_jsonl(path)

    record = result.records[0]
    assert isinstance(record, WorkflowRunRecord)
    assert record.raw["api_key"] == REDACTED
    assert "abc123" not in str(record.raw)
    assert "secret-token" not in str(record.raw)
    assert REDACTED in str(record.raw)


def test_parse_approval_requests_jsonl_happy_path(tmp_path: Path) -> None:
    """Parse valid Project 1 approval request JSONL."""
    path = tmp_path / "approval-requests.jsonl"
    _write_jsonl(path, [_approval_payload("approval-001", status="pending")])

    result = parse_approval_requests_jsonl(path)

    assert result.ok
    record = result.records[0]
    assert isinstance(record, ApprovalRequestRecord)
    assert record.approval_id == "approval-001"
    assert record.status is ApprovalStatus.PENDING


def test_parse_approval_requests_jsonl_status_filter(tmp_path: Path) -> None:
    """Filter approval requests by normalized status."""
    path = tmp_path / "approval-requests.jsonl"
    _write_jsonl(
        path,
        [
            _approval_payload("approval-pending", status="pending"),
            _approval_payload("approval-approved", status="approved"),
        ],
    )

    result = parse_approval_requests_jsonl(path, status_filter="approved")

    assert result.ok
    approval_ids = [
        record.approval_id
        for record in result.records
        if isinstance(record, ApprovalRequestRecord)
    ]
    assert approval_ids == ["approval-approved"]


def test_parse_approval_requests_jsonl_missing_file(tmp_path: Path) -> None:
    """Return a warning when approval requests JSONL is missing."""
    result = parse_approval_requests_jsonl(tmp_path / "missing.jsonl")

    assert result.ok
    assert result.warnings[0].code == "missing_file"


def test_parse_markdown_report_happy_path(tmp_path: Path) -> None:
    """Extract supported counts and sections from a deterministic report."""
    path = tmp_path / "daily-marketing-report-20260528T120000Z.md"
    path.write_text(_report_text(), encoding="utf-8")

    result = parse_markdown_report(path)

    assert result.ok
    record = result.records[0]
    assert isinstance(record, ReportSummaryRecord)
    assert record.campaigns_processed == 2
    assert record.critical_findings == 1
    assert record.warning_findings == 3
    assert record.campaigns_requiring_human_review == 1
    assert all(record.required_sections.values())


def test_parse_markdown_report_missing_section_warnings(tmp_path: Path) -> None:
    """Warn when deterministic report sections are missing."""
    path = tmp_path / "report.md"
    path.write_text(
        "# Daily Marketing Operations Report\n\nGenerated timestamp: 2026-05-28T12:00:00+00:00\n",
        encoding="utf-8",
    )

    result = parse_markdown_report(path)

    assert result.ok
    assert any(warning.code == "missing_report_section" for warning in result.warnings)


def test_parse_markdown_report_missing_file(tmp_path: Path) -> None:
    """Return a warning when a Markdown report is missing."""
    result = parse_markdown_report(tmp_path / "missing.md")

    assert result.ok
    assert result.warnings[0].code == "missing_file"


def test_parse_tool_evidence_json_happy_path(tmp_path: Path) -> None:
    """Parse saved Project 2 CLI JSON evidence."""
    path = tmp_path / "tool-evidence.json"
    path.write_text(
        json.dumps({"tool_name": "generate_demo_brief", "status": "ok", "ready": True}),
        encoding="utf-8",
    )

    result = parse_tool_evidence_json(path)

    assert result.ok
    record = result.records[0]
    assert isinstance(record, ToolEvidenceRecord)
    assert record.tool_name == "generate_demo_brief"
    assert record.ready is True


def test_parse_tool_evidence_json_malformed_json(tmp_path: Path) -> None:
    """Return an explicit error when tool evidence JSON is malformed."""
    path = tmp_path / "tool-evidence.json"
    path.write_text("{not-json", encoding="utf-8")

    result = parse_tool_evidence_json(path)

    assert not result.ok
    assert result.errors[0].code == "malformed_json"


def test_parse_guardrail_output_text_extracts_pass_fail_block(tmp_path: Path) -> None:
    """Extract simple guardrail pass, fail and block status signals."""
    passed = tmp_path / "passed.txt"
    failed = tmp_path / "failed.txt"
    blocked = tmp_path / "blocked.txt"
    passed.write_text("guardrail checks passed clean\n", encoding="utf-8")
    failed.write_text("guardrail failure: diff check failed\n", encoding="utf-8")
    blocked.write_text("blocked destructive command intent\n", encoding="utf-8")

    pass_result = parse_guardrail_output_text(passed)
    fail_result = parse_guardrail_output_text(failed)
    block_result = parse_guardrail_output_text(blocked)

    pass_record = pass_result.records[0]
    fail_record = fail_result.records[0]
    block_record = block_result.records[0]
    assert isinstance(pass_record, GuardrailEvidenceRecord)
    assert isinstance(fail_record, GuardrailEvidenceRecord)
    assert isinstance(block_record, GuardrailEvidenceRecord)
    assert pass_record.status is GuardrailStatus.PASSED
    assert fail_record.status is GuardrailStatus.FAILED
    assert block_record.status is GuardrailStatus.BLOCKED


def test_ingest_local_agentops_sources_combines_multiple_sources(tmp_path: Path) -> None:
    """Combine records from every provided local source."""
    run_history = tmp_path / "workflow-runs.jsonl"
    approvals = tmp_path / "approval-requests.jsonl"
    report = tmp_path / "report.md"
    tool = tmp_path / "tool.json"
    guardrail = tmp_path / "guardrail.txt"
    _write_jsonl(run_history, [_run_payload("run-001")])
    _write_jsonl(approvals, [_approval_payload("approval-001")])
    report.write_text(_report_text(), encoding="utf-8")
    tool.write_text(json.dumps({"tool": "check_runtime_clean", "status": "ok"}), encoding="utf-8")
    guardrail.write_text("passed\n", encoding="utf-8")

    result = ingest_local_agentops_sources(
        run_history_path=run_history,
        approval_requests_path=approvals,
        markdown_report_path=report,
        tool_evidence_json_path=tool,
        guardrail_output_text_path=guardrail,
    )

    assert result.ok
    assert result.record_count == 5


def test_run_history_ordering_is_deterministic(tmp_path: Path) -> None:
    """Preserve source order and apply limits deterministically."""
    path = tmp_path / "workflow-runs.jsonl"
    _write_jsonl(
        path,
        [_run_payload("run-b"), _run_payload("run-a"), _run_payload("run-c")],
    )

    result = parse_run_history_jsonl(path, limit=2)

    run_ids = [
        record.run_id for record in result.records if isinstance(record, WorkflowRunRecord)
    ]
    assert run_ids == ["run-b", "run-a"]


def test_sanitize_value_redacts_secret_keys_and_inline_values() -> None:
    """Redact obvious secret-like keys and inline credential text."""
    sanitized = sanitize_value(
        {
            "api_key": "abc123",
            "message": "Authorization: Bearer token-value and password=secret",
        }
    )

    assert sanitized["api_key"] == REDACTED
    assert "abc123" not in str(sanitized)
    assert "token-value" not in str(sanitized)
    assert "secret" not in str(sanitized)


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


def _run_payload(
    run_id: str,
    *,
    status: str = "succeeded",
    failure_message: str | None = None,
) -> dict[str, object]:
    """Build a sample Project 1 run-history payload.

    Args:
        run_id: Workflow run identifier.
        status: Workflow status.
        failure_message: Optional failure message.

    Returns:
        Sample run-history payload.
    """
    return {
        "run_id": run_id,
        "workflow_name": "daily_marketing_report",
        "status": status,
        "started_at": "2026-05-28T12:00:00+00:00",
        "finished_at": "2026-05-28T12:00:03+00:00",
        "duration_seconds": 3.0,
        "report_path": f"reports/{run_id}.md",
        "snapshot_count": 2,
        "finding_count": 1,
        "critical_finding_count": 0,
        "human_review_required": False,
        "approval_request_count": 0,
        "notification_status": "skipped",
        "notification_count": 0,
        "created_task_ids": ["task-001"],
        "task_error_count": 0,
        "data_quality_summary": {"missing_campaign_metadata": 1},
        "failure_type": None,
        "failure_message": failure_message,
    }


def _approval_payload(approval_id: str, *, status: str = "pending") -> dict[str, object]:
    """Build a sample Project 1 approval request payload.

    Args:
        approval_id: Approval request identifier.
        status: Approval request status.

    Returns:
        Sample approval request payload.
    """
    return {
        "approval_id": approval_id,
        "run_id": "daily-marketing-report-20260528T120000Z",
        "campaign_id": "cmp-search-brand",
        "source": "deterministic_finding",
        "source_reference": "cmp-search-brand:negative_roi",
        "risk_level": "high",
        "status": status,
        "title": "Pause campaign",
        "rationale": "Critical deterministic finding requires human approval.",
        "source_evidence": {"severity": "critical"},
        "created_at": "2026-05-28T12:00:00+00:00",
        "decision": None,
    }


def _report_text() -> str:
    """Return a representative deterministic Project 1 Markdown report.

    Returns:
        Markdown report text.
    """
    return """# Daily Marketing Operations Report

Generated timestamp: 2026-05-28T12:00:00+00:00

## Executive Summary
- Campaigns processed: 2.
- Healthy campaigns: 1.
- Critical findings: 1.
- Warning findings: 3.
- Informational findings: 0.
- Campaigns requiring human review: 1.

## Campaign Health Overview
| Campaign ID | Status | Critical | Warning | Info | Human Review |
| --- | --- | --- | --- | --- | --- |
| cmp-search-brand | critical | 1 | 0 | 0 | yes |

## Critical Anomalies
- `cmp-search-brand` negative_roi: ROI below threshold; human review: yes.

## Warning Anomalies
- `cmp-social` cpa_above_threshold: CPA above threshold; human review: no.

## Data Quality Issues
- No data quality issues detected.

## Human Review Required
- `cmp-search-brand`: critical finding.

## Campaign Snapshot Table
| Campaign ID | Name | Channel | Human Review |
| --- | --- | --- | --- |
| cmp-search-brand | Brand Search | search | yes |

## Deterministic Recommended Actions
- `cmp-search-brand`: Review campaign performance.

## Limitations
- Local deterministic report only.
"""
