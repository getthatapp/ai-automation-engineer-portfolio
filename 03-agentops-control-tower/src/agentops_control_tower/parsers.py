"""Deterministic parsers for local AgentOps evidence files."""

from __future__ import annotations

import json
import re
from collections.abc import Iterable
from datetime import datetime
from json import JSONDecodeError
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from agentops_control_tower.models import (
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
from agentops_control_tower.sanitization import redact_text, sanitize_mapping

REQUIRED_REPORT_SECTIONS: tuple[str, ...] = (
    "Executive Summary",
    "Campaign Health Overview",
    "Critical Anomalies",
    "Warning Anomalies",
    "Data Quality Issues",
    "Human Review Required",
    "Campaign Snapshot Table",
    "Deterministic Recommended Actions",
    "Limitations",
)

_REPORT_COUNT_PATTERNS: dict[str, re.Pattern[str]] = {
    "campaigns_processed": re.compile(r"(?im)^-\s+Campaigns processed:\s+(\d+)\."),
    "critical_findings": re.compile(r"(?im)^-\s+Critical findings:\s+(\d+)\."),
    "warning_findings": re.compile(r"(?im)^-\s+Warning findings:\s+(\d+)\."),
    "campaigns_requiring_human_review": re.compile(
        r"(?im)^-\s+Campaigns requiring human review:\s+(\d+)\."
    ),
}
_GENERATED_TIMESTAMP_PATTERN = re.compile(r"(?im)^Generated timestamp:\s+(.+?)\s*$")
_PASSED_PATTERN = re.compile(r"(?i)\b(pass|passed|clean|ok)\b")
_FAILED_PATTERN = re.compile(r"(?i)\b(fail|failed|failure|error)\b")
_BLOCKED_PATTERN = re.compile(r"(?i)\b(block|blocked|denied)\b")


def parse_run_history_jsonl(path: str | Path, limit: int | None = None) -> IngestionResult:
    """Parse Project 1 workflow run-history JSONL.

    Args:
        path: Local JSONL file path.
        limit: Optional maximum number of successfully parsed records to return.

    Returns:
        Typed ingestion result with workflow run records, warnings or errors.
    """
    source_path = Path(path)
    if limit is not None and limit < 0:
        return _result_with_error(
            IngestionSourceType.RUN_HISTORY,
            source_path,
            "invalid_limit",
            "limit must be greater than or equal to zero",
        )
    payloads, warnings, errors = _read_jsonl(source_path, IngestionSourceType.RUN_HISTORY)
    records: list[WorkflowRunRecord] = []
    if not errors:
        for line_number, payload in payloads:
            if limit is not None and len(records) >= limit:
                break
            try:
                records.append(_workflow_run_from_payload(payload))
            except ValidationError:
                errors.append(
                    _error(
                        IngestionSourceType.RUN_HISTORY,
                        source_path,
                        "validation_error",
                        "Run history record failed validation.",
                        line_number,
                    )
                )
    return IngestionResult(
        source_type=IngestionSourceType.RUN_HISTORY,
        records=tuple(records),
        warnings=tuple(warnings),
        errors=tuple(errors),
    )


def parse_approval_requests_jsonl(
    path: str | Path,
    status_filter: ApprovalStatus | str | None = None,
) -> IngestionResult:
    """Parse Project 1 approval request JSONL.

    Args:
        path: Local approval request JSONL file path.
        status_filter: Optional approval status to include.

    Returns:
        Typed ingestion result with approval request records, warnings or errors.
    """
    source_path = Path(path)
    normalized_filter = _approval_status(status_filter) if status_filter is not None else None
    if normalized_filter is ApprovalStatus.UNKNOWN and status_filter is not None:
        return _result_with_error(
            IngestionSourceType.APPROVAL_REQUESTS,
            source_path,
            "invalid_status_filter",
            "status_filter must be pending, approved, rejected or expired",
        )

    payloads, warnings, errors = _read_jsonl(source_path, IngestionSourceType.APPROVAL_REQUESTS)
    records: list[ApprovalRequestRecord] = []
    if not errors:
        for line_number, payload in payloads:
            try:
                record = _approval_request_from_payload(payload)
            except ValidationError:
                errors.append(
                    _error(
                        IngestionSourceType.APPROVAL_REQUESTS,
                        source_path,
                        "validation_error",
                        "Approval request record failed validation.",
                        line_number,
                    )
                )
                continue
            if normalized_filter is None or record.status is normalized_filter:
                records.append(record)
    return IngestionResult(
        source_type=IngestionSourceType.APPROVAL_REQUESTS,
        records=tuple(records),
        warnings=tuple(warnings),
        errors=tuple(errors),
    )


def parse_markdown_report(path: str | Path) -> IngestionResult:
    """Parse a Project 1 deterministic Markdown report summary.

    Args:
        path: Local Markdown report path.

    Returns:
        Typed ingestion result with one report summary record, warnings or errors.
    """
    source_path = Path(path)
    if not source_path.exists():
        return _missing_file_result(IngestionSourceType.MARKDOWN_REPORT, source_path)
    text = source_path.read_text(encoding="utf-8")
    required_sections = {
        section: f"## {section}" in text for section in REQUIRED_REPORT_SECTIONS
    }
    warnings = [
        _warning(
            IngestionSourceType.MARKDOWN_REPORT,
            source_path,
            "missing_report_section",
            f"Required report section is missing: {section}",
        )
        for section, present in required_sections.items()
        if not present
    ]
    try:
        record = ReportSummaryRecord(
            path=source_path,
            generated_timestamp=_extract_generated_timestamp(text),
            campaigns_processed=_extract_count(text, "campaigns_processed"),
            critical_findings=_extract_count(text, "critical_findings"),
            warning_findings=_extract_count(text, "warning_findings"),
            campaigns_requiring_human_review=_extract_count(
                text,
                "campaigns_requiring_human_review",
            ),
            required_sections=required_sections,
        )
    except ValidationError:
        return _result_with_error(
            IngestionSourceType.MARKDOWN_REPORT,
            source_path,
            "validation_error",
            "Markdown report summary failed validation.",
        )
    return IngestionResult(
        source_type=IngestionSourceType.MARKDOWN_REPORT,
        records=(record,),
        warnings=tuple(warnings),
    )


def parse_tool_evidence_json(path: str | Path) -> IngestionResult:
    """Parse saved Project 2 CLI JSON evidence.

    Args:
        path: Local JSON evidence file path.

    Returns:
        Typed ingestion result with one tool evidence record, warnings or errors.
    """
    source_path = Path(path)
    if not source_path.exists():
        return _missing_file_result(IngestionSourceType.TOOL_EVIDENCE, source_path)
    try:
        decoded = json.loads(source_path.read_text(encoding="utf-8"))
    except JSONDecodeError:
        return _result_with_error(
            IngestionSourceType.TOOL_EVIDENCE,
            source_path,
            "malformed_json",
            "Tool evidence JSON could not be decoded.",
        )
    if not isinstance(decoded, dict):
        return _result_with_error(
            IngestionSourceType.TOOL_EVIDENCE,
            source_path,
            "invalid_json_shape",
            "Tool evidence JSON must be an object.",
        )
    payload = sanitize_mapping(decoded)
    try:
        record = ToolEvidenceRecord(
            path=source_path,
            tool_name=_optional_str(payload.get("tool_name") or payload.get("tool")),
            status=_optional_str(payload.get("status")),
            ready=payload.get("ready") if isinstance(payload.get("ready"), bool) else None,
            payload=payload,
        )
    except ValidationError:
        return _result_with_error(
            IngestionSourceType.TOOL_EVIDENCE,
            source_path,
            "validation_error",
            "Tool evidence record failed validation.",
        )
    return IngestionResult(source_type=IngestionSourceType.TOOL_EVIDENCE, records=(record,))


def parse_guardrail_output_text(path: str | Path) -> IngestionResult:
    """Parse saved Project 2 guardrail output text.

    Args:
        path: Local guardrail output text path.

    Returns:
        Typed ingestion result with one guardrail evidence record, warnings or errors.
    """
    source_path = Path(path)
    if not source_path.exists():
        return _missing_file_result(IngestionSourceType.GUARDRAIL_OUTPUT, source_path)
    text = redact_text(source_path.read_text(encoding="utf-8"))
    lines = text.splitlines()
    status, signals = _guardrail_status(text)
    excerpt = "\n".join(lines[:5])
    try:
        record = GuardrailEvidenceRecord(
            path=source_path,
            status=status,
            matched_signals=signals,
            line_count=len(lines),
            excerpt=excerpt,
        )
    except ValidationError:
        return _result_with_error(
            IngestionSourceType.GUARDRAIL_OUTPUT,
            source_path,
            "validation_error",
            "Guardrail output record failed validation.",
        )
    return IngestionResult(source_type=IngestionSourceType.GUARDRAIL_OUTPUT, records=(record,))


def _read_jsonl(
    path: Path,
    source_type: IngestionSourceType,
) -> tuple[list[tuple[int, dict[str, Any]]], list[IngestionWarning], list[IngestionError]]:
    """Read a JSONL file into sanitized dictionaries.

    Args:
        path: Local JSONL path.
        source_type: Source type associated with the file.

    Returns:
        Tuple of parsed payloads, warnings and errors.
    """
    if not path.exists():
        result = _missing_file_result(source_type, path)
        return [], list(result.warnings), list(result.errors)

    payloads: list[tuple[int, dict[str, Any]]] = []
    errors: list[IngestionError] = []
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            errors.append(
                _error(source_type, path, "malformed_jsonl", "JSONL line is blank.", line_number)
            )
            continue
        try:
            decoded = json.loads(line)
        except JSONDecodeError:
            errors.append(
                _error(
                    source_type,
                    path,
                    "malformed_jsonl",
                    "JSONL line could not be decoded.",
                    line_number,
                )
            )
            continue
        if not isinstance(decoded, dict):
            errors.append(
                _error(
                    source_type,
                    path,
                    "invalid_jsonl_shape",
                    "JSONL line must be an object.",
                    line_number,
                )
            )
            continue
        payloads.append((line_number, sanitize_mapping(decoded)))
    return payloads, [], errors


def _workflow_run_from_payload(payload: dict[str, Any]) -> WorkflowRunRecord:
    """Build a workflow run record from a sanitized source payload.

    Args:
        payload: Sanitized run-history payload.

    Returns:
        Normalized workflow run record.
    """
    return WorkflowRunRecord(
        run_id=str(payload.get("run_id") or "").strip(),
        workflow_name=str(payload.get("workflow_name") or "unknown").strip(),
        status=_workflow_status(payload.get("status")),
        started_at=_datetime_or_none(payload.get("started_at")),
        finished_at=_datetime_or_none(payload.get("finished_at")),
        duration_seconds=_float_or_none(payload.get("duration_seconds")),
        report_path=_path_or_none(payload.get("report_path")),
        snapshot_count=_int_or_none(payload.get("snapshot_count")),
        finding_count=_int_or_none(payload.get("finding_count")),
        critical_finding_count=_int_or_none(payload.get("critical_finding_count")),
        human_review_required=_bool_or_none(payload.get("human_review_required")),
        approval_request_count=_int_or_none(payload.get("approval_request_count")),
        notification_status=_optional_str(payload.get("notification_status")),
        notification_count=_int_or_none(payload.get("notification_count")),
        created_task_ids=_tuple_of_str(payload.get("created_task_ids")),
        task_error_count=_int_or_none(payload.get("task_error_count")),
        data_quality_summary=_dict_or_empty(payload.get("data_quality_summary")),
        failure_type=_optional_str(payload.get("failure_type")),
        failure_message=_optional_str(payload.get("failure_message")),
        raw=payload,
    )


def _approval_request_from_payload(payload: dict[str, Any]) -> ApprovalRequestRecord:
    """Build an approval request record from a sanitized source payload.

    Args:
        payload: Sanitized approval request payload.

    Returns:
        Normalized approval request record.
    """
    return ApprovalRequestRecord(
        approval_id=str(payload.get("approval_id") or "").strip(),
        run_id=_optional_str(payload.get("run_id")),
        campaign_id=_optional_str(payload.get("campaign_id")),
        source=_optional_str(payload.get("source")),
        source_reference=_optional_str(payload.get("source_reference")),
        risk_level=_optional_str(payload.get("risk_level")),
        status=_approval_status(payload.get("status")),
        title=_optional_str(payload.get("title")),
        rationale=_optional_str(payload.get("rationale")),
        created_at=_datetime_or_none(payload.get("created_at")),
        decision=_dict_or_none(payload.get("decision")),
        source_evidence=_dict_or_empty(payload.get("source_evidence")),
        raw=payload,
    )


def _workflow_status(value: Any) -> WorkflowStatus:
    """Normalize a raw workflow status value.

    Args:
        value: Raw status value.

    Returns:
        Known workflow status or `UNKNOWN`.
    """
    try:
        return WorkflowStatus(str(value).strip().lower())
    except ValueError:
        return WorkflowStatus.UNKNOWN


def _approval_status(value: Any) -> ApprovalStatus:
    """Normalize a raw approval status value.

    Args:
        value: Raw status value.

    Returns:
        Known approval status or `UNKNOWN`.
    """
    try:
        return ApprovalStatus(str(value).strip().lower())
    except ValueError:
        return ApprovalStatus.UNKNOWN


def _guardrail_status(text: str) -> tuple[GuardrailStatus, tuple[str, ...]]:
    """Extract simple guardrail status signals from text.

    Args:
        text: Sanitized guardrail output text.

    Returns:
        Status and matched signal names.
    """
    signals: list[str] = []
    if _BLOCKED_PATTERN.search(text):
        signals.append("blocked")
    if _FAILED_PATTERN.search(text):
        signals.append("failed")
    if _PASSED_PATTERN.search(text):
        signals.append("passed")

    if "blocked" in signals:
        return GuardrailStatus.BLOCKED, tuple(signals)
    if "failed" in signals:
        return GuardrailStatus.FAILED, tuple(signals)
    if "passed" in signals:
        return GuardrailStatus.PASSED, tuple(signals)
    return GuardrailStatus.UNKNOWN, ()


def _extract_generated_timestamp(text: str) -> datetime | None:
    """Extract a generated timestamp from Markdown text.

    Args:
        text: Markdown report text.

    Returns:
        Parsed timestamp when present and valid, otherwise `None`.
    """
    match = _GENERATED_TIMESTAMP_PATTERN.search(text)
    if not match:
        return None
    return _datetime_or_none(match.group(1))


def _extract_count(text: str, key: str) -> int | None:
    """Extract a known executive summary count from Markdown text.

    Args:
        text: Markdown report text.
        key: Count pattern key.

    Returns:
        Parsed count when present, otherwise `None`.
    """
    pattern = _REPORT_COUNT_PATTERNS[key]
    match = pattern.search(text)
    if not match:
        return None
    return int(match.group(1))


def _datetime_or_none(value: Any) -> datetime | None:
    """Parse a datetime value when possible.

    Args:
        value: Raw datetime-like value.

    Returns:
        Parsed datetime or `None`.
    """
    if isinstance(value, datetime):
        return value
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _path_or_none(value: Any) -> Path | None:
    """Convert a raw path value into a `Path` when present.

    Args:
        value: Raw path-like value.

    Returns:
        Path or `None`.
    """
    if isinstance(value, str) and value.strip():
        return Path(value.strip())
    return None


def _optional_str(value: Any) -> str | None:
    """Convert a raw value to stripped optional text.

    Args:
        value: Raw value.

    Returns:
        Stripped text or `None`.
    """
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _int_or_none(value: Any) -> int | None:
    """Convert a raw value to int when possible.

    Args:
        value: Raw value.

    Returns:
        Integer or `None`.
    """
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value)
    return None


def _float_or_none(value: Any) -> float | None:
    """Convert a raw value to float when possible.

    Args:
        value: Raw value.

    Returns:
        Float or `None`.
    """
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return None
    return None


def _bool_or_none(value: Any) -> bool | None:
    """Convert a raw value to bool when possible.

    Args:
        value: Raw value.

    Returns:
        Boolean or `None`.
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "yes", "1"}:
            return True
        if normalized in {"false", "no", "0"}:
            return False
    return None


def _tuple_of_str(value: Any) -> tuple[str, ...]:
    """Convert a raw sequence to a tuple of non-empty strings.

    Args:
        value: Raw sequence.

    Returns:
        Tuple of stripped text values.
    """
    if not isinstance(value, Iterable) or isinstance(value, (str, bytes, bytearray, dict)):
        return ()
    return tuple(str(item).strip() for item in value if str(item).strip())


def _dict_or_empty(value: Any) -> dict[str, Any]:
    """Return a dictionary when the value has dictionary shape.

    Args:
        value: Raw value.

    Returns:
        Dictionary or empty dictionary.
    """
    return value if isinstance(value, dict) else {}


def _dict_or_none(value: Any) -> dict[str, Any] | None:
    """Return a dictionary or `None`.

    Args:
        value: Raw value.

    Returns:
        Dictionary or `None`.
    """
    return value if isinstance(value, dict) else None


def _missing_file_result(source_type: IngestionSourceType, path: Path) -> IngestionResult:
    """Build a warning-only missing file result.

    Args:
        source_type: Source type associated with the missing file.
        path: Missing path.

    Returns:
        Warning-only ingestion result.
    """
    return IngestionResult(
        source_type=source_type,
        warnings=(
            _warning(source_type, path, "missing_file", "Optional ingestion source is missing."),
        ),
    )


def _result_with_error(
    source_type: IngestionSourceType,
    path: Path,
    code: str,
    message: str,
    line_number: int | None = None,
) -> IngestionResult:
    """Build an error-only ingestion result.

    Args:
        source_type: Source type associated with the error.
        path: Source path.
        code: Error code.
        message: Sanitized error message.
        line_number: Optional line number.

    Returns:
        Error-only ingestion result.
    """
    return IngestionResult(
        source_type=source_type,
        errors=(_error(source_type, path, code, message, line_number),),
    )


def _warning(
    source_type: IngestionSourceType,
    path: Path,
    code: str,
    message: str,
) -> IngestionWarning:
    """Build a typed ingestion warning.

    Args:
        source_type: Source type.
        path: Source path.
        code: Warning code.
        message: Warning message.

    Returns:
        Typed ingestion warning.
    """
    return IngestionWarning(source_type=source_type, path=path, code=code, message=message)


def _error(
    source_type: IngestionSourceType,
    path: Path,
    code: str,
    message: str,
    line_number: int | None = None,
) -> IngestionError:
    """Build a typed ingestion error.

    Args:
        source_type: Source type.
        path: Source path.
        code: Error code.
        message: Error message.
        line_number: Optional line number.

    Returns:
        Typed ingestion error.
    """
    return IngestionError(
        source_type=source_type,
        path=path,
        code=code,
        message=message,
        line_number=line_number,
    )
