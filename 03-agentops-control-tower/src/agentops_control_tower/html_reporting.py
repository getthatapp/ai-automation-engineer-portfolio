"""Deterministic static HTML reporting for local AgentOps views."""

from __future__ import annotations

from datetime import datetime
from html import escape
from pathlib import Path
from typing import Any

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


def render_agentops_html_report(view: AgentOpsControlTowerView) -> str:
    """Render a deterministic static HTML report for a local control tower view.

    Args:
        view: Combined local ingestion, summary and timeline view.

    Returns:
        Self-contained HTML report text derived only from typed local evidence.
    """
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            "<title>AgentOps Control Tower Report</title>",
            "<style>",
            _style_text(),
            "</style>",
            "</head>",
            "<body>",
            '<main class="report">',
            "<header>",
            "<h1>AgentOps Control Tower Report</h1>",
            (
                '<p class="meta">Generated timestamp / source timestamp: '
                f"{_html_text(_generated_timestamp(view))}</p>"
            ),
            "</header>",
            _section("Input Source Paths", _source_path_list(view)),
            _section(
                "Overall Health Status",
                _unordered_list([f"Status: {view.summary.overall_status.value}"]),
            ),
            _section("Workflow Summary", _workflow_summary_list(view)),
            _section("Approval Summary", _approval_summary_list(view)),
            _section("Report Health Summary", _report_health_summary_list(view)),
            _section("Tool Evidence Summary", _tool_evidence_summary_list(view)),
            _section("Guardrail Summary", _guardrail_summary_list(view)),
            _section("Ingestion Warnings", _warning_list(view.ingestion_result.warnings)),
            _section("Ingestion Errors", _error_list(view.ingestion_result.errors)),
            _section("Timeline", _timeline_list(view.timeline.events)),
            _section(
                "Deterministic Recommended Actions",
                _recommended_action_list(view.summary.recommended_actions),
            ),
            _section("Limitations / Missing Data", _limitation_list(view)),
            "</main>",
            "</body>",
            "</html>",
            "",
        ]
    )


def _style_text() -> str:
    """Return static inline CSS for the local report.

    Returns:
        CSS text with no external asset references.
    """
    return """
:root {
  color-scheme: light;
  font-family: Arial, Helvetica, sans-serif;
  background: #f7f8fa;
  color: #1f2933;
}
body {
  margin: 0;
}
.report {
  max-width: 1040px;
  margin: 0 auto;
  padding: 32px 20px 48px;
}
header {
  border-bottom: 2px solid #d5d9e0;
  margin-bottom: 24px;
  padding-bottom: 16px;
}
h1 {
  font-size: 32px;
  line-height: 1.2;
  margin: 0 0 8px;
}
h2 {
  border-bottom: 1px solid #d5d9e0;
  font-size: 20px;
  margin: 28px 0 12px;
  padding-bottom: 6px;
}
.meta {
  color: #52606d;
  margin: 0;
}
ul {
  margin: 0;
  padding-left: 22px;
}
li {
  margin: 6px 0;
}
code {
  background: #e8edf3;
  border-radius: 4px;
  padding: 1px 4px;
}
.empty {
  color: #66788a;
}
""".strip()


def _section(title: str, body: str) -> str:
    """Wrap section body HTML with a heading.

    Args:
        title: Static section title.
        body: Already escaped body HTML.

    Returns:
        Section HTML.
    """
    return "\n".join(
        [
            "<section>",
            f"<h2>{_html_text(title)}</h2>",
            body,
            "</section>",
        ]
    )


def _generated_timestamp(view: AgentOpsControlTowerView) -> str:
    """Return a deterministic report timestamp.

    Args:
        view: Combined local ingestion, summary and timeline view.

    Returns:
        Earliest parsed source report timestamp, or `Unavailable`.
    """
    timestamps = sorted(
        record.generated_timestamp
        for record in view.ingestion_result.records
        if isinstance(record, ReportSummaryRecord) and record.generated_timestamp is not None
    )
    if not timestamps:
        return "Unavailable"
    return _datetime_text(timestamps[0])


def _source_path_list(view: AgentOpsControlTowerView) -> str:
    """Build escaped HTML for source paths.

    Args:
        view: Combined local ingestion, summary and timeline view.

    Returns:
        Unordered list HTML.
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
        return _empty_paragraph("No local source paths were provided.")
    return _unordered_list(
        [f"{source_type}: {path}" for source_type, path in sorted(paths)]
    )


def _workflow_summary_list(view: AgentOpsControlTowerView) -> str:
    """Build escaped HTML for workflow summary counts.

    Args:
        view: Combined local ingestion, summary and timeline view.

    Returns:
        Unordered list HTML.
    """
    summary = view.summary.workflow_runs
    items = [
        f"Total workflow runs: {summary.total}",
        f"Failed workflow runs: {summary.failed_count}",
        f"Workflow runs requiring human review: {summary.human_review_required_count}",
    ]
    items.extend(_status_items("Workflow status", summary.by_status))
    return _unordered_list(items)


def _approval_summary_list(view: AgentOpsControlTowerView) -> str:
    """Build escaped HTML for approval summary counts.

    Args:
        view: Combined local ingestion, summary and timeline view.

    Returns:
        Unordered list HTML.
    """
    summary = view.summary.approvals
    items = [
        f"Total approval requests: {summary.total}",
        f"Pending approval requests: {summary.pending_count}",
    ]
    items.extend(_status_items("Approval status", summary.by_status))
    return _unordered_list(items)


def _report_health_summary_list(view: AgentOpsControlTowerView) -> str:
    """Build escaped HTML for report health summary counts.

    Args:
        view: Combined local ingestion, summary and timeline view.

    Returns:
        Unordered list HTML.
    """
    summary = view.summary.reports
    return _unordered_list(
        [
            f"Parsed reports: {summary.total}",
            f"Reports requiring human review: {summary.requiring_human_review_count}",
            f"Reports with missing required sections: {summary.missing_required_section_count}",
        ]
    )


def _tool_evidence_summary_list(view: AgentOpsControlTowerView) -> str:
    """Build escaped HTML for tool evidence summary counts.

    Args:
        view: Combined local ingestion, summary and timeline view.

    Returns:
        Unordered list HTML.
    """
    summary = view.summary.tools
    return _unordered_list(
        [
            f"Tool evidence records: {summary.total}",
            f"Ready tool evidence records: {summary.ready_count}",
            f"Not-ready tool evidence records: {summary.not_ready_count}",
        ]
    )


def _guardrail_summary_list(view: AgentOpsControlTowerView) -> str:
    """Build escaped HTML for guardrail summary counts.

    Args:
        view: Combined local ingestion, summary and timeline view.

    Returns:
        Unordered list HTML.
    """
    summary = view.summary.guardrails
    items = [
        f"Guardrail records: {summary.total}",
        f"Failed or blocked guardrail records: {summary.failed_or_blocked_count}",
    ]
    items.extend(_status_items("Guardrail status", summary.by_status))
    return _unordered_list(items)


def _warning_list(warnings: tuple[IngestionWarning, ...]) -> str:
    """Build escaped HTML for ingestion warnings.

    Args:
        warnings: Ingestion warnings from local parsing.

    Returns:
        Unordered list HTML or empty-state paragraph.
    """
    if not warnings:
        return _empty_paragraph("None.")
    return _unordered_list(
        [
            (
                f"{warning.source_type.value} {warning.code} at "
                f"{_path_text(warning.path)}: {warning.message}"
            )
            for warning in warnings
        ]
    )


def _error_list(errors: tuple[IngestionError, ...]) -> str:
    """Build escaped HTML for ingestion errors.

    Args:
        errors: Ingestion errors from local parsing.

    Returns:
        Unordered list HTML or empty-state paragraph.
    """
    if not errors:
        return _empty_paragraph("None.")
    items: list[str] = []
    for error in errors:
        line_detail = "" if error.line_number is None else f" line {error.line_number}"
        items.append(
            f"{error.source_type.value} {error.code} at "
            f"{_path_text(error.path)}{line_detail}: {error.message}"
        )
    return _unordered_list(items)


def _timeline_list(events: tuple[AgentOpsTimelineEvent, ...]) -> str:
    """Build escaped HTML for timeline events.

    Args:
        events: Timeline events in deterministic timeline order.

    Returns:
        Unordered list HTML or empty-state paragraph.
    """
    if not events:
        return _empty_paragraph("No timeline events were generated from provided local sources.")
    return _unordered_list(
        [
            (
                f"{_datetime_text(event.timestamp)} | {event.event_type.value} | "
                f"{event.severity.value} | {event.title} ({_event_identifier(event)})"
            )
            for event in events
        ]
    )


def _recommended_action_list(actions: tuple[str, ...]) -> str:
    """Build escaped HTML for deterministic recommended actions.

    Args:
        actions: Deterministic recommended actions from the summary.

    Returns:
        Unordered list HTML or empty-state paragraph.
    """
    if not actions:
        return _empty_paragraph("No deterministic recommended actions were generated.")
    return _unordered_list(list(actions))


def _limitation_list(view: AgentOpsControlTowerView) -> str:
    """Build escaped HTML for report limitations and missing data.

    Args:
        view: Combined local ingestion, summary and timeline view.

    Returns:
        Unordered list HTML.
    """
    limitations = [
        "No hosted dashboard is implemented in this local milestone.",
        (
            "No web server, database, scheduler, background service or external "
            "integration is implemented."
        ),
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
    return _unordered_list(limitations)


def _status_items(prefix: str, statuses: dict[Any, int]) -> list[str]:
    """Build status count text items.

    Args:
        prefix: Label prefix for each status item.
        statuses: Enum-keyed status count dictionary.

    Returns:
        Text items in existing mapping order.
    """
    return [
        f"{prefix} {getattr(status, 'value', str(status))}: {count}"
        for status, count in statuses.items()
    ]


def _unordered_list(items: list[str]) -> str:
    """Build escaped unordered-list HTML.

    Args:
        items: Plain text list items.

    Returns:
        Escaped unordered list HTML.
    """
    lines = ["<ul>"]
    lines.extend(f"<li>{_html_text(item)}</li>" for item in items)
    lines.append("</ul>")
    return "\n".join(lines)


def _empty_paragraph(text: str) -> str:
    """Build an escaped empty-state paragraph.

    Args:
        text: Plain text empty-state message.

    Returns:
        Escaped paragraph HTML.
    """
    return f'<p class="empty">{_html_text(text)}</p>'


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


def _html_text(value: str) -> str:
    """Escape text for safe HTML output.

    Args:
        value: Plain text value.

    Returns:
        Escaped HTML text.
    """
    return escape(value, quote=True)
