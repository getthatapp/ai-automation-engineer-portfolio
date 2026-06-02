"""Deterministic local read-only tools for Project 1 artifact inspection."""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from agent_toolkit_mcp.errors import InvalidPathError
from agent_toolkit_mcp.models import (
    CheckRuntimeCleanInput,
    CheckRuntimeCleanResult,
    GenerateDemoBriefInput,
    GenerateDemoBriefResult,
    JsonLineError,
    ListPendingApprovalsInput,
    ListPendingApprovalsResult,
    PendingApprovalSummary,
    ReadRunHistoryInput,
    ReadRunHistoryResult,
    ValidateReportInput,
    ValidateReportResult,
)
from agent_toolkit_mcp.path_safety import (
    ensure_child_path,
    resolve_existing_directory,
    resolve_existing_file,
    resolve_optional_file,
    safe_relative_path,
)

REQUIRED_REPORT_SECTIONS = [
    "Executive Summary",
    "Campaign Health Overview",
    "Critical Anomalies",
    "Warning Anomalies",
    "Data Quality Issues",
    "Human Review Required",
    "Campaign Snapshot Table",
    "Deterministic Recommended Actions",
    "Limitations / Missing Data",
]

RUNTIME_PATTERNS = [
    "reports/daily-marketing-report-*.md",
    "run-history/workflow-runs.jsonl",
    "approval-requests/approval-requests.jsonl",
    "__pycache__/",
    "*.pyc",
]

EXPECTED_PROJECT_1_PATHS = [
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

DEMO_COMMANDS = [
    "uv sync",
    "uv run playwright install chromium",
    "./scripts/start_services.sh",
    "./scripts/run_workflow.sh",
    "./scripts/run_workflow_with_llm.sh",
    "NOTIFICATION_DELIVERY_ENABLED=true ./scripts/run_workflow.sh",
    "./scripts/run_checks.sh",
]

SECRET_KEY_PATTERN = re.compile(
    r"(api[_-]?key|authorization|bearer|credential|password|secret|token)",
    re.IGNORECASE,
)
SECRET_VALUE_PATTERN = re.compile(
    r"(bearer\s+[A-Za-z0-9._~+/-]+|sk-[A-Za-z0-9_-]+|xox[baprs]-[A-Za-z0-9-]+)",
    re.IGNORECASE,
)
REDACTED = "[REDACTED]"


def validate_report(report_path: str | Path) -> ValidateReportResult:
    """Validate that a deterministic Markdown report contains required sections.

    Args:
        report_path: Path to a local Markdown report.

    Returns:
        Structured validation result with missing sections and validity flag.
    """

    input_model = ValidateReportInput(report_path=Path(report_path))
    resolved = input_model.report_path.expanduser().resolve(strict=False)
    try:
        report_file = resolve_existing_file(input_model.report_path, expected_suffix=".md")
    except InvalidPathError as exc:
        return ValidateReportResult(
            valid=False,
            report_path=str(resolved),
            file_exists=resolved.exists(),
            required_sections=REQUIRED_REPORT_SECTIONS,
            found_sections=[],
            missing_sections=REQUIRED_REPORT_SECTIONS,
            errors=[str(exc)],
        )

    content = report_file.read_text(encoding="utf-8")
    found_sections = _extract_markdown_sections(content)
    missing_sections = [
        section for section in REQUIRED_REPORT_SECTIONS if section not in found_sections
    ]
    return ValidateReportResult(
        valid=not missing_sections,
        report_path=str(report_file),
        file_exists=True,
        required_sections=REQUIRED_REPORT_SECTIONS,
        found_sections=found_sections,
        missing_sections=missing_sections,
    )


def read_run_history(jsonl_path: str | Path, limit: int = 5) -> ReadRunHistoryResult:
    """Read recent workflow run history records from local JSONL.

    Args:
        jsonl_path: Path to a workflow run history JSONL file.
        limit: Maximum number of recent valid records to return.

    Returns:
        Structured result containing recent sanitized records and malformed line errors.
    """

    input_model = ReadRunHistoryInput(jsonl_path=Path(jsonl_path), limit=limit)
    resolved = input_model.jsonl_path.expanduser().resolve(strict=False)
    try:
        history_file = resolve_optional_file(input_model.jsonl_path)
    except InvalidPathError as exc:
        return ReadRunHistoryResult(
            jsonl_path=str(resolved),
            file_exists=resolved.exists(),
            records=[],
            malformed_lines=[],
            errors=[str(exc)],
        )
    if not history_file.exists():
        return ReadRunHistoryResult(
            jsonl_path=str(history_file),
            file_exists=False,
            records=[],
            malformed_lines=[],
        )

    records, malformed_lines = _read_jsonl(history_file)
    return ReadRunHistoryResult(
        jsonl_path=str(history_file),
        file_exists=True,
        records=[_sanitize_value(record) for record in records[-input_model.limit :]],
        malformed_lines=malformed_lines,
    )


def list_pending_approvals(jsonl_path: str | Path) -> ListPendingApprovalsResult:
    """List pending approval summaries from a local approval JSONL file.

    Args:
        jsonl_path: Path to a local approval request JSONL file.

    Returns:
        Structured result containing sanitized pending approval summaries.
    """

    input_model = ListPendingApprovalsInput(jsonl_path=Path(jsonl_path))
    resolved = input_model.jsonl_path.expanduser().resolve(strict=False)
    try:
        approvals_file = resolve_optional_file(input_model.jsonl_path)
    except InvalidPathError as exc:
        return ListPendingApprovalsResult(
            jsonl_path=str(resolved),
            file_exists=resolved.exists(),
            pending_approvals=[],
            malformed_lines=[],
            errors=[str(exc)],
        )
    if not approvals_file.exists():
        return ListPendingApprovalsResult(
            jsonl_path=str(approvals_file),
            file_exists=False,
            pending_approvals=[],
            malformed_lines=[],
        )

    records, malformed_lines = _read_jsonl(approvals_file)
    pending_approvals = []
    for record in records:
        sanitized_record = _sanitize_value(record)
        if sanitized_record.get("status") != "pending":
            continue
        pending_approvals.append(
            PendingApprovalSummary(
                approval_id=_optional_string(sanitized_record.get("approval_id")),
                run_id=_optional_string(sanitized_record.get("run_id")),
                campaign_id=_optional_string(sanitized_record.get("campaign_id")),
                source=_optional_string(sanitized_record.get("source")),
                source_reference=_optional_string(sanitized_record.get("source_reference")),
                risk_level=_optional_string(sanitized_record.get("risk_level")),
                status=_optional_string(sanitized_record.get("status")),
                title=_optional_string(sanitized_record.get("title")),
                created_at=_optional_string(sanitized_record.get("created_at")),
            )
        )

    return ListPendingApprovalsResult(
        jsonl_path=str(approvals_file),
        file_exists=True,
        pending_approvals=pending_approvals,
        malformed_lines=malformed_lines,
    )


def check_runtime_clean(project_path: str | Path) -> CheckRuntimeCleanResult:
    """Check whether generated Project 1 runtime files are present.

    Args:
        project_path: Path to the Project 1 directory.

    Returns:
        Structured cleanliness result with found generated artifact paths.
    """

    input_model = CheckRuntimeCleanInput(project_path=Path(project_path))
    resolved = input_model.project_path.expanduser().resolve(strict=False)
    try:
        project_dir = resolve_existing_directory(input_model.project_path)
    except InvalidPathError as exc:
        return CheckRuntimeCleanResult(
            clean=False,
            project_path=str(resolved),
            found_paths=[],
            checked_patterns=RUNTIME_PATTERNS,
            errors=[str(exc)],
        )

    found_paths: set[str] = set()
    _collect_glob_matches(project_dir, "reports/daily-marketing-report-*.md", found_paths)
    _collect_explicit_file(project_dir, "run-history/workflow-runs.jsonl", found_paths)
    _collect_explicit_file(project_dir, "approval-requests/approval-requests.jsonl", found_paths)
    _collect_glob_matches(project_dir, "**/__pycache__", found_paths, directories_only=True)
    _collect_glob_matches(project_dir, "**/*.pyc", found_paths)

    sorted_paths = sorted(found_paths)
    return CheckRuntimeCleanResult(
        clean=not sorted_paths,
        project_path=str(project_dir),
        found_paths=sorted_paths,
        checked_patterns=RUNTIME_PATTERNS,
    )


def generate_demo_brief(project_path: str | Path) -> GenerateDemoBriefResult:
    """Generate a deterministic summary of Project 1 local demo readiness.

    Args:
        project_path: Path to the Project 1 directory.

    Returns:
        Structured demo readiness result with deterministic text and local commands.
    """

    input_model = GenerateDemoBriefInput(project_path=Path(project_path))
    resolved = input_model.project_path.expanduser().resolve(strict=False)
    try:
        project_dir = resolve_existing_directory(input_model.project_path)
    except InvalidPathError as exc:
        return GenerateDemoBriefResult(
            project_path=str(resolved),
            ready=False,
            brief=f"Project 1 demo readiness could not be checked: {exc}",
            present_paths=[],
            missing_paths=EXPECTED_PROJECT_1_PATHS,
            local_commands=DEMO_COMMANDS,
            errors=[str(exc)],
        )

    present_paths: list[str] = []
    missing_paths: list[str] = []
    for relative_path in EXPECTED_PROJECT_1_PATHS:
        child_path = ensure_child_path(project_dir / relative_path, project_dir)
        if child_path.exists():
            present_paths.append(relative_path)
        else:
            missing_paths.append(relative_path)

    ready = not missing_paths
    status = "ready" if ready else "not ready"
    brief_lines = [
        f"Project 1 demo readiness: {status}.",
        f"Present expected files: {len(present_paths)}.",
        f"Missing expected files: {len(missing_paths)}.",
        "Local demo commands:",
        *[f"- {command}" for command in DEMO_COMMANDS],
        "This brief is deterministic, local-only and does not call an LLM or external API.",
    ]
    return GenerateDemoBriefResult(
        project_path=str(project_dir),
        ready=ready,
        brief="\n".join(brief_lines),
        present_paths=present_paths,
        missing_paths=missing_paths,
        local_commands=DEMO_COMMANDS,
    )


def _extract_markdown_sections(content: str) -> list[str]:
    """Extract level-two Markdown headings from report text.

    Args:
        content: Markdown content to inspect.

    Returns:
        Ordered section names without leading hash markers.
    """

    sections: list[str] = []
    for line in content.splitlines():
        if not line.startswith("## "):
            continue
        section = line.removeprefix("## ").strip()
        if section:
            sections.append(section)
    return sections


def _read_jsonl(path: Path) -> tuple[list[dict[str, Any]], list[JsonLineError]]:
    """Read JSON object records from a JSONL file.

    Args:
        path: Existing JSONL file to read.

    Returns:
        Tuple of valid object records and malformed line errors.
    """

    records: list[dict[str, Any]] = []
    malformed_lines: list[JsonLineError] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError as exc:
            malformed_lines.append(JsonLineError(line_number=line_number, message=str(exc)))
            continue
        if not isinstance(parsed, dict):
            malformed_lines.append(
                JsonLineError(line_number=line_number, message="JSONL line is not an object")
            )
            continue
        records.append(parsed)
    return records, malformed_lines


def _sanitize_value(value: Any, *, parent_key: str | None = None) -> Any:
    """Redact secret-like keys and values from nested data.

    Args:
        value: Value to sanitize.
        parent_key: Key associated with the value when available.

    Returns:
        Sanitized value safe for tool output.
    """

    if parent_key is not None and SECRET_KEY_PATTERN.search(parent_key):
        return REDACTED
    if isinstance(value, dict):
        return {str(key): _sanitize_value(item, parent_key=str(key)) for key, item in value.items()}
    if isinstance(value, list):
        return [_sanitize_value(item) for item in value]
    if isinstance(value, str) and SECRET_VALUE_PATTERN.search(value):
        return REDACTED
    return value


def _optional_string(value: Any) -> str | None:
    """Convert a value into an optional string for summary models.

    Args:
        value: Value to convert.

    Returns:
        String value or `None`.
    """

    if value is None:
        return None
    return str(value)


def _collect_explicit_file(project_dir: Path, relative_path: str, found_paths: set[str]) -> None:
    """Collect an explicit child file when it exists.

    Args:
        project_dir: Validated project directory.
        relative_path: Relative file path to check.
        found_paths: Mutable set receiving safe relative paths.
    """

    candidate = ensure_child_path(project_dir / relative_path, project_dir)
    if candidate.is_file():
        found_paths.add(safe_relative_path(candidate, project_dir))


def _collect_glob_matches(
    project_dir: Path,
    pattern: str,
    found_paths: set[str],
    *,
    directories_only: bool = False,
) -> None:
    """Collect glob matches below a project directory.

    Args:
        project_dir: Validated project directory.
        pattern: Glob pattern to evaluate under the project directory.
        found_paths: Mutable set receiving safe relative paths.
        directories_only: Whether to include only directories.
    """

    for candidate in project_dir.glob(pattern):
        safe_candidate = ensure_child_path(candidate, project_dir)
        if directories_only and not safe_candidate.is_dir():
            continue
        found_paths.add(safe_relative_path(safe_candidate, project_dir))


def call_tool(tool_name: str, arguments: dict[str, Any]) -> Any:
    """Call a deterministic local tool by registered name.

    Args:
        tool_name: Name of the registered tool.
        arguments: Keyword arguments for the tool.

    Returns:
        Tool result model.

    Raises:
        KeyError: If the requested tool is not registered.
        ValidationError: If arguments fail Pydantic input validation.
    """

    registry: dict[str, Callable[..., Any]] = {
        "validate_report": validate_report,
        "read_run_history": read_run_history,
        "list_pending_approvals": list_pending_approvals,
        "check_runtime_clean": check_runtime_clean,
        "generate_demo_brief": generate_demo_brief,
    }
    try:
        tool = registry[tool_name]
    except KeyError as exc:
        raise KeyError(f"Unknown tool: {tool_name}") from exc
    try:
        return tool(**arguments)
    except ValidationError:
        raise
