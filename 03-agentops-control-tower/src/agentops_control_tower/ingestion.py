"""Aggregation entry points for local AgentOps evidence ingestion."""

from __future__ import annotations

from pathlib import Path

from agentops_control_tower.models import (
    ApprovalStatus,
    IngestionResult,
    IngestionSourceType,
)
from agentops_control_tower.parsers import (
    parse_approval_requests_jsonl,
    parse_guardrail_output_text,
    parse_markdown_report,
    parse_run_history_jsonl,
    parse_tool_evidence_json,
)


def ingest_local_agentops_sources(
    *,
    run_history_path: str | Path | None = None,
    approval_requests_path: str | Path | None = None,
    markdown_report_path: str | Path | None = None,
    tool_evidence_json_path: str | Path | None = None,
    guardrail_output_text_path: str | Path | None = None,
    run_history_limit: int | None = None,
    approval_status_filter: ApprovalStatus | str | None = None,
) -> IngestionResult:
    """Ingest provided local AgentOps source files into one combined result.

    Args:
        run_history_path: Optional Project 1 run-history JSONL path.
        approval_requests_path: Optional Project 1 approval requests JSONL path.
        markdown_report_path: Optional Project 1 Markdown report path.
        tool_evidence_json_path: Optional saved Project 2 CLI JSON evidence path.
        guardrail_output_text_path: Optional saved Project 2 guardrail output path.
        run_history_limit: Optional run-history record limit.
        approval_status_filter: Optional approval status filter.

    Returns:
        Combined ingestion result containing records, warnings and errors from
        only the source paths provided.
    """
    results: list[IngestionResult] = []
    if run_history_path is not None:
        results.append(parse_run_history_jsonl(run_history_path, limit=run_history_limit))
    if approval_requests_path is not None:
        results.append(
            parse_approval_requests_jsonl(
                approval_requests_path,
                status_filter=approval_status_filter,
            )
        )
    if markdown_report_path is not None:
        results.append(parse_markdown_report(markdown_report_path))
    if tool_evidence_json_path is not None:
        results.append(parse_tool_evidence_json(tool_evidence_json_path))
    if guardrail_output_text_path is not None:
        results.append(parse_guardrail_output_text(guardrail_output_text_path))

    return IngestionResult(
        source_type=IngestionSourceType.COMBINED,
        records=tuple(record for result in results for record in result.records),
        warnings=tuple(warning for result in results for warning in result.warnings),
        errors=tuple(error for result in results for error in result.errors),
    )
