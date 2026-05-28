"""Prompt construction for safe LLM interpretation of deterministic outputs."""

import json
from collections.abc import Mapping, Sequence
from typing import Any

from marketing_ops_agent.aggregation import CampaignSnapshot
from marketing_ops_agent.anomaly import AnomalyFinding
from marketing_ops_agent.llm.models import LLMInterpretationRequest
from marketing_ops_agent.observability import WorkflowRunRecord, sanitize_observability_text

PROMPT_VERSION = "marketing-ops-interpretation-v1"
MAX_REPORT_SUMMARY_CHARS = 4_000


def build_interpretation_prompt(request: LLMInterpretationRequest) -> str:
    """Build a provider-agnostic prompt from validated deterministic objects only."""

    payload = {
        "prompt_version": PROMPT_VERSION,
        "campaign_snapshots": [_snapshot_payload(snapshot) for snapshot in request.snapshots],
        "deterministic_findings": [_finding_payload(finding) for finding in request.findings],
        "deterministic_report_summary": _sanitize_text(
            request.deterministic_report_summary[:MAX_REPORT_SUMMARY_CHARS]
        ),
        "workflow_run": (
            None if request.workflow_run is None else _workflow_run_payload(request.workflow_run)
        ),
    }
    return "\n".join(
        [
            "You are interpreting a deterministic marketing operations report.",
            "",
            "Safety and accuracy rules:",
            "- Use only the validated deterministic data in the JSON payload below.",
            "- Never invent missing metrics, campaign names, source data, trends or causes.",
            (
                "- If a metric or source is missing, preserve it as missing and "
                "mention the limitation."
            ),
            "- Preserve data quality flags exactly; do not downgrade or remove them.",
            "- Treat human_review_required flags as blocking sensitive automated action.",
            "- Keep deterministic facts separate from recommendations.",
            "- Do not overwrite, suppress or recalculate deterministic anomaly findings.",
            "- Do not request, reveal or infer credentials, secrets, tokens or API keys.",
            (
                "- Recommendations must cite the deterministic finding or data "
                "quality flag they depend on."
            ),
            "",
            "Return structured JSON compatible with LLMInterpretationResult fields.",
            "",
            "Validated deterministic payload:",
            json.dumps(_sanitize_value(payload), indent=2, sort_keys=True),
        ]
    )


def _snapshot_payload(snapshot: CampaignSnapshot) -> dict[str, Any]:
    return {
        "campaign_id": snapshot.campaign_id,
        "campaign_name": snapshot.scraped_row.name,
        "channel": snapshot.scraped_row.channel.value,
        "validated_panel_metrics": {
            "impressions": snapshot.scraped_row.impressions,
            "clicks": snapshot.scraped_row.clicks,
            "conversions": snapshot.scraped_row.conversions,
            "spend": snapshot.scraped_row.cost,
            "revenue": snapshot.scraped_row.revenue,
        },
        "campaign_metadata": (
            "missing"
            if snapshot.campaign_metadata is None
            else {
                "name": snapshot.campaign_metadata.name,
                "channel": snapshot.campaign_metadata.channel.value,
                "metrics": {
                    "impressions": snapshot.campaign_metadata.metrics.impressions,
                    "clicks": snapshot.campaign_metadata.metrics.clicks,
                    "conversions": snapshot.campaign_metadata.metrics.conversions,
                    "spend": snapshot.campaign_metadata.metrics.spend,
                    "revenue": snapshot.campaign_metadata.metrics.revenue,
                },
                "collected_at": snapshot.campaign_metadata.collected_at.isoformat(),
            }
        ),
        "analytics_metrics": (
            "missing"
            if snapshot.analytics_metrics is None
            else {
                "impressions": snapshot.analytics_metrics.impressions,
                "clicks": snapshot.analytics_metrics.clicks,
                "conversions": snapshot.analytics_metrics.conversions,
                "cost": snapshot.analytics_metrics.cost,
                "revenue": snapshot.analytics_metrics.revenue,
            }
        ),
        "data_quality_flags": [flag.value for flag in snapshot.data_quality_flags],
        "data_quality_notes": list(snapshot.data_quality_notes),
        "requires_human_review": snapshot.requires_human_review,
        "aggregated_at": snapshot.aggregated_at.isoformat(),
    }


def _finding_payload(finding: AnomalyFinding) -> dict[str, Any]:
    return {
        "campaign_id": finding.campaign_id,
        "anomaly_type": finding.anomaly_type.value,
        "severity": finding.severity.value,
        "message": finding.message,
        "source": finding.source,
        "source_evidence": dict(sorted(finding.source_evidence.items())),
        "requires_human_review": finding.requires_human_review,
    }


def _workflow_run_payload(record: WorkflowRunRecord) -> dict[str, Any]:
    return {
        "run_id": record.run_id,
        "workflow_name": record.workflow_name,
        "status": record.status.value,
        "started_at": record.started_at.isoformat(),
        "finished_at": record.finished_at.isoformat(),
        "duration_seconds": record.duration_seconds,
        "report_path": None if record.report_path is None else str(record.report_path),
        "snapshot_count": record.snapshot_count,
        "finding_count": record.finding_count,
        "critical_finding_count": record.critical_finding_count,
        "human_review_required": record.human_review_required,
        "task_error_count": record.task_error_count,
        "data_quality_summary": record.data_quality_summary,
        "failure_type": record.failure_type,
        "failure_message": record.failure_message,
    }


def _sanitize_value(value: object) -> object:
    if isinstance(value, str):
        return _sanitize_text(value)
    if isinstance(value, Mapping):
        return {str(key): _sanitize_value(item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, bytes | bytearray):
        return [_sanitize_value(item) for item in value]
    return value


def _sanitize_text(value: str) -> str:
    return sanitize_observability_text(value).replace("\x00", "")
