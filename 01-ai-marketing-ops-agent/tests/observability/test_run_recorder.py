from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from marketing_ops_agent.models import WorkflowStatus
from marketing_ops_agent.observability import (
    LocalRunRecorder,
    MalformedRunRecordLineError,
    WorkflowRunRecord,
)

STARTED_AT = datetime(2026, 5, 28, 12, 0, tzinfo=UTC)


def test_appends_successful_run_record_and_creates_storage_directory(
    tmp_path: Path,
) -> None:
    path = tmp_path / "nested" / "workflow-runs.jsonl"
    recorder = LocalRunRecorder(path)
    record = _record(run_id="run-001")

    recorder.append(record)

    assert path.exists()
    assert recorder.read_recent() == [record]


def test_reads_recent_records_in_chronological_order(tmp_path: Path) -> None:
    recorder = LocalRunRecorder(tmp_path / "workflow-runs.jsonl")
    records = [
        _record(run_id="run-001", started_offset=0),
        _record(run_id="run-002", started_offset=1),
        _record(run_id="run-003", started_offset=2),
    ]
    for record in records:
        recorder.append(record)

    assert recorder.read_recent(limit=2) == records[1:]


def test_reads_run_by_run_id(tmp_path: Path) -> None:
    recorder = LocalRunRecorder(tmp_path / "workflow-runs.jsonl")
    expected = _record(run_id="run-002", started_offset=1)
    recorder.append(_record(run_id="run-001"))
    recorder.append(expected)

    assert recorder.get("run-002") == expected


def test_missing_run_id_returns_none(tmp_path: Path) -> None:
    recorder = LocalRunRecorder(tmp_path / "workflow-runs.jsonl")
    recorder.append(_record(run_id="run-001"))

    assert recorder.get("missing-run") is None
    assert recorder.get("   ") is None


def test_missing_history_file_reads_as_empty(tmp_path: Path) -> None:
    recorder = LocalRunRecorder(tmp_path / "missing" / "workflow-runs.jsonl")

    assert recorder.read_recent() == []
    assert recorder.get("run-001") is None


def test_malformed_jsonl_line_raises_explicit_error(tmp_path: Path) -> None:
    path = tmp_path / "workflow-runs.jsonl"
    recorder = LocalRunRecorder(path)
    recorder.append(_record(run_id="run-001"))
    path.write_text(
        f"{path.read_text(encoding='utf-8')}not-json\n",
        encoding="utf-8",
    )

    with pytest.raises(MalformedRunRecordLineError) as exc_info:
        recorder.read_recent()

    assert exc_info.value.path == path
    assert exc_info.value.line_number == 2
    assert exc_info.value.reason == "invalid JSON"


def test_secret_like_failure_text_is_redacted_before_storage(tmp_path: Path) -> None:
    path = tmp_path / "workflow-runs.jsonl"
    recorder = LocalRunRecorder(path)
    record = _record(
        run_id="run-failed",
        status=WorkflowStatus.FAILED,
        failure_type="scrape_marketing_panel",
        failure_message=(
            "request failed password=super-secret token=abc123 "
            "Authorization=Bearer raw-token Bearer second-token"
        ),
    )

    recorder.append(record)

    raw_history = path.read_text(encoding="utf-8")
    stored_record = recorder.get("run-failed")
    assert "super-secret" not in raw_history
    assert "abc123" not in raw_history
    assert "raw-token" not in raw_history
    assert "second-token" not in raw_history
    assert stored_record is not None
    assert stored_record.failure_message is not None
    assert "[REDACTED]" in stored_record.failure_message


def _record(
    *,
    run_id: str,
    status: WorkflowStatus = WorkflowStatus.SUCCEEDED,
    started_offset: int = 0,
    failure_type: str | None = None,
    failure_message: str | None = None,
) -> WorkflowRunRecord:
    started_at = STARTED_AT + timedelta(minutes=started_offset)
    finished_at = started_at + timedelta(seconds=3)
    return WorkflowRunRecord(
        run_id=run_id,
        workflow_name="daily_marketing_report",
        status=status,
        started_at=started_at,
        finished_at=finished_at,
        duration_seconds=3.0,
        report_path=Path("reports") / f"{run_id}.md",
        snapshot_count=2,
        finding_count=1,
        critical_finding_count=0,
        human_review_required=False,
        created_task_ids=("task-001",),
        task_error_count=0,
        data_quality_summary={"missing_campaign_metadata": 1},
        failure_type=failure_type,
        failure_message=failure_message,
    )
