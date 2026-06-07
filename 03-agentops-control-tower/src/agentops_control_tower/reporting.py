"""Deterministic Markdown reporting for local AgentOps views."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from agentops_control_tower.display_paths import format_display_path
from agentops_control_tower.models import (
    AgentOpsControlTowerView,
    AgentOpsTimelineEvent,
    GuardrailEvidenceRecord,
    IngestionError,
    IngestionWarning,
    ReportSummaryRecord,
    ToolEvidenceRecord,
    WorkflowRunRecord,
)


def render_agentops_markdown_report(view: AgentOpsControlTowerView) -> str:
    """Render a deterministic Markdown report for a local control tower view.

    Args:
        view: Combined local ingestion, summary and timeline view.

    Returns:
        Markdown report text derived only from typed local evidence.
    """
    lines: list[str] = [
        "# AgentOps Control Tower Report",
        "",
        f"Generated timestamp: {_generated_timestamp(view)}",
        "",
        "## Input Source Paths",
        *_source_path_lines(view),
        "",
        "## Overall Health Status",
        f"- Status: `{view.summary.overall_status.value}`",
        "",
        "## Workflow Summary",
        f"- Total workflow runs: {view.summary.workflow_runs.total}",
        f"- Failed workflow runs: {view.summary.workflow_runs.failed_count}",
        (
            "- Workflow runs requiring human review: "
            f"{view.summary.workflow_runs.human_review_required_count}"
        ),
        *_status_lines("Workflow status", view.summary.workflow_runs.by_status),
        "",
        "## Approval Summary",
        f"- Total approval requests: {view.summary.approvals.total}",
        f"- Pending approval requests: {view.summary.approvals.pending_count}",
        *_status_lines("Approval status", view.summary.approvals.by_status),
        "",
        "## Report Health Summary",
        f"- Parsed reports: {view.summary.reports.total}",
        (
            "- Reports requiring human review: "
            f"{view.summary.reports.requiring_human_review_count}"
        ),
        (
            "- Reports with missing required sections: "
            f"{view.summary.reports.missing_required_section_count}"
        ),
        "",
        "## Tool Evidence Summary",
        f"- Tool evidence records: {view.summary.tools.total}",
        f"- Ready tool evidence records: {view.summary.tools.ready_count}",
        f"- Not-ready tool evidence records: {view.summary.tools.not_ready_count}",
        "",
        "## Guardrail Summary",
        f"- Guardrail records: {view.summary.guardrails.total}",
        (
            "- Failed or blocked guardrail records: "
            f"{view.summary.guardrails.failed_or_blocked_count}"
        ),
        *_status_lines("Guardrail status", view.summary.guardrails.by_status),
        "",
        "## Ingestion Warnings",
        *_warning_lines(view.ingestion_result.warnings),
        "",
        "## Ingestion Errors",
        *_error_lines(view.ingestion_result.errors),
        "",
        "## Timeline",
        *_timeline_lines(view.timeline.events),
        "",
        "## Deterministic Recommended Actions",
        *_recommended_action_lines(view.summary.recommended_actions),
        "",
        "## Limitations / Missing Data",
        *_limitation_lines(view),
        "",
    ]
    return "\n".join(lines)


def _generated_timestamp(view: AgentOpsControlTowerView) -> str:
    """Return a deterministic generated timestamp for the report.

    Args:
        view: Combined local ingestion, summary and timeline view.

    Returns:
        Earliest parsed source report timestamp, or an explicit unavailable value.
    """
    timestamps = sorted(
        record.generated_timestamp
        for record in view.ingestion_result.records
        if isinstance(record, ReportSummaryRecord) and record.generated_timestamp is not None
    )
    if not timestamps:
        return "Unavailable from provided local sources"
    return _datetime_text(timestamps[0])


def _source_path_lines(view: AgentOpsControlTowerView) -> list[str]:
    """Build source path lines from typed records, warnings and errors.

    Args:
        view: Combined local ingestion, summary and timeline view.

    Returns:
        Markdown bullet lines with stable source path ordering.
    """
    paths: set[tuple[str, str]] = set()
    for source_type, path in view.input_paths.items():
        paths.add((source_type.value, format_display_path(path)))

    for record in view.ingestion_result.records:
        if isinstance(record, WorkflowRunRecord) and record.report_path is not None:
            paths.add(("workflow_report_reference", format_display_path(record.report_path)))
        elif isinstance(record, ReportSummaryRecord):
            paths.add(("markdown_report", format_display_path(record.path)))
        elif isinstance(record, ToolEvidenceRecord):
            paths.add(("tool_evidence", format_display_path(record.path)))
        elif isinstance(record, GuardrailEvidenceRecord):
            paths.add(("guardrail_output", format_display_path(record.path)))

    for warning in view.ingestion_result.warnings:
        if warning.path is not None:
            paths.add((warning.source_type.value, format_display_path(warning.path)))
    for error in view.ingestion_result.errors:
        if error.path is not None:
            paths.add((error.source_type.value, format_display_path(error.path)))

    if not paths:
        return ["- No local source paths were provided."]
    return [f"- `{source_type}`: `{path}`" for source_type, path in sorted(paths)]


def _status_lines(prefix: str, statuses: object) -> list[str]:
    """Build Markdown lines for enum-keyed status count dictionaries.

    Args:
        prefix: Label prefix for each status line.
        statuses: Mapping-like object containing enum keys and integer counts.

    Returns:
        Markdown bullet lines in existing mapping order.
    """
    if not isinstance(statuses, dict):
        return []
    return [
        f"- {prefix} `{getattr(status, 'value', str(status))}`: {count}"
        for status, count in statuses.items()
    ]


def _warning_lines(warnings: tuple[IngestionWarning, ...]) -> list[str]:
    """Build Markdown warning lines.

    Args:
        warnings: Ingestion warnings from local parsing.

    Returns:
        Markdown bullet lines, or a clear empty-state line.
    """
    if not warnings:
        return ["- None."]
    return [
        (
            f"- `{warning.source_type.value}` `{warning.code}` at "
            f"`{_path_text(warning.path)}`: {warning.message}"
        )
        for warning in warnings
    ]


def _error_lines(errors: tuple[IngestionError, ...]) -> list[str]:
    """Build Markdown ingestion error lines.

    Args:
        errors: Ingestion errors from local parsing.

    Returns:
        Markdown bullet lines, or a clear empty-state line.
    """
    if not errors:
        return ["- None."]
    lines: list[str] = []
    for error in errors:
        line_detail = "" if error.line_number is None else f" line {error.line_number}"
        lines.append(
            f"- `{error.source_type.value}` `{error.code}` at "
            f"`{_path_text(error.path)}`{line_detail}: {error.message}"
        )
    return lines


def _timeline_lines(events: tuple[AgentOpsTimelineEvent, ...]) -> list[str]:
    """Build Markdown timeline lines.

    Args:
        events: Timeline events in deterministic timeline order.

    Returns:
        Markdown bullet lines, or a clear empty-state line.
    """
    if not events:
        return ["- No timeline events were generated from provided local sources."]
    return [
        (
            f"- `{_datetime_text(event.timestamp)}` `{event.event_type.value}` "
            f"`{event.severity.value}` {event.title} (`{_event_identifier(event)}`)"
        )
        for event in events
    ]


def _recommended_action_lines(actions: tuple[str, ...]) -> list[str]:
    """Build Markdown recommended action lines.

    Args:
        actions: Deterministic recommended actions from the summary.

    Returns:
        Markdown bullet lines, or a clear empty-state line.
    """
    if not actions:
        return ["- No deterministic recommended actions were generated."]
    return [f"- {action}" for action in actions]


def _limitation_lines(view: AgentOpsControlTowerView) -> list[str]:
    """Build deterministic limitations and missing-data lines.

    Args:
        view: Combined local ingestion, summary and timeline view.

    Returns:
        Markdown bullet lines describing unavailable local signals.
    """
    limitations = [
        "No dashboard/UI is implemented in this local milestone.",
        "No database, scheduler, background service or external integration is implemented.",
        "No deployed AgentOps platform is claimed by this report.",
        "The report uses only provided local files and deterministic parsing.",
    ]
    if view.summary.workflow_runs.total == 0:
        limitations.append("No workflow run-history records were available.")
    if view.summary.approvals.total == 0:
        limitations.append("No approval request records were available.")
    if view.summary.reports.total == 0:
        limitations.append("No deterministic Markdown report summary was available.")
    if view.summary.tools.total == 0:
        limitations.append("No saved Project 2 tool evidence was available.")
    if view.summary.guardrails.total == 0:
        limitations.append("No saved guardrail output was available.")
    return [f"- {limitation}" for limitation in limitations]


def _datetime_text(value: datetime | None) -> str:
    """Return stable text for an optional datetime.

    Args:
        value: Optional timestamp.

    Returns:
        ISO-8601 timestamp text or `Unavailable`.
    """
    if value is None:
        return "Unavailable"
    return value.isoformat()


def _event_identifier(event: AgentOpsTimelineEvent) -> str:
    """Return display text for a timeline event identifier.

    Args:
        event: Timeline event.

    Returns:
        Project-relative identifier for local file-backed events, otherwise the
        original identifier.
    """
    if event.source_type.value in {
        "markdown_report",
        "tool_evidence",
        "guardrail_output",
    }:
        return format_display_path(event.identifier)
    return event.identifier


def _path_text(path: Path | None) -> str:
    """Return stable text for an optional path.

    Args:
        path: Optional local path.

    Returns:
        Path text or `Unavailable`.
    """
    return "Unavailable" if path is None else format_display_path(path)
