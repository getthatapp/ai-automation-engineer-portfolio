"""Deterministic Markdown report writer for campaign snapshots and findings."""

from collections import Counter
from collections.abc import Sequence

from marketing_ops_agent.aggregation.campaign_snapshot import CampaignSnapshot
from marketing_ops_agent.aggregation.data_quality import DataQualityFlag
from marketing_ops_agent.anomaly.models import AnomalyFinding, AnomalySeverity, AnomalyType
from marketing_ops_agent.reporting.models import ReportMetadata
from marketing_ops_agent.reporting.templates import bullet, heading, table

SEVERITY_ORDER: dict[AnomalySeverity, int] = {
    AnomalySeverity.CRITICAL: 0,
    AnomalySeverity.WARNING: 1,
    AnomalySeverity.INFO: 2,
}

DATA_QUALITY_ANOMALY_TYPES: frozenset[AnomalyType] = frozenset(
    {
        AnomalyType.MISSING_CAMPAIGN_METADATA,
        AnomalyType.MISSING_ANALYTICS_METRICS,
        AnomalyType.SPEND_MISMATCH,
        AnomalyType.CONVERSIONS_MISMATCH,
        AnomalyType.REVENUE_MISMATCH,
        AnomalyType.STALE_DATA,
        AnomalyType.REQUIRES_HUMAN_REVIEW,
    }
)


class MarkdownReportWriter:
    """Render deterministic Markdown from validated campaign business objects."""

    def write(
        self,
        snapshots: Sequence[CampaignSnapshot],
        findings: Sequence[AnomalyFinding],
        metadata: ReportMetadata | None = None,
    ) -> str:
        """Return a complete Markdown report.

        The writer consumes only aggregated snapshots and typed anomaly findings.
        It does not read raw scraped rows, raw REST responses or raw GraphQL
        responses.
        """

        resolved_metadata = metadata or ReportMetadata()
        sorted_snapshots = sorted(snapshots, key=lambda snapshot: snapshot.campaign_id)
        sorted_findings = sort_findings(findings)

        sections = [
            heading(1, resolved_metadata.title),
            f"Generated timestamp: {resolved_metadata.generated_at.isoformat()}",
            self._render_executive_summary(sorted_snapshots, sorted_findings),
            self._render_health_overview(sorted_snapshots, sorted_findings),
            self._render_findings_section(
                "Critical Anomalies",
                sorted_findings,
                AnomalySeverity.CRITICAL,
            ),
            self._render_findings_section(
                "Warning Anomalies",
                sorted_findings,
                AnomalySeverity.WARNING,
            ),
            self._render_data_quality(sorted_snapshots, sorted_findings),
            self._render_human_review(sorted_snapshots, sorted_findings),
            self._render_snapshot_table(sorted_snapshots),
            self._render_recommended_actions(sorted_findings),
            self._render_limitations(sorted_snapshots),
        ]
        return "\n\n".join(sections) + "\n"

    def _render_executive_summary(
        self,
        snapshots: Sequence[CampaignSnapshot],
        findings: Sequence[AnomalyFinding],
    ) -> str:
        severity_counts = Counter(finding.severity for finding in findings)
        healthy_campaigns = [
            snapshot
            for snapshot in snapshots
            if _is_healthy_campaign(snapshot, findings_for_campaign(findings, snapshot.campaign_id))
        ]
        review_campaign_ids = sorted(_campaign_ids_requiring_review(snapshots, findings))

        lines = [
            heading(2, "Executive Summary"),
            bullet(f"Campaigns processed: {len(snapshots)}."),
            bullet(f"Healthy campaigns: {len(healthy_campaigns)}."),
            bullet(f"Critical findings: {severity_counts[AnomalySeverity.CRITICAL]}."),
            bullet(f"Warning findings: {severity_counts[AnomalySeverity.WARNING]}."),
            bullet(f"Informational findings: {severity_counts[AnomalySeverity.INFO]}."),
            bullet(f"Campaigns requiring human review: {len(review_campaign_ids)}."),
        ]
        if len(healthy_campaigns) == len(snapshots) and not findings:
            lines.append(
                bullet(
                    "All campaigns are healthy based on available deterministic snapshots "
                    "and anomaly findings."
                )
            )
        return "\n".join(lines)

    def _render_health_overview(
        self,
        snapshots: Sequence[CampaignSnapshot],
        findings: Sequence[AnomalyFinding],
    ) -> str:
        rows: list[list[str]] = []
        for snapshot in snapshots:
            campaign_findings = findings_for_campaign(findings, snapshot.campaign_id)
            severity_counts = Counter(finding.severity for finding in campaign_findings)
            rows.append(
                [
                    snapshot.campaign_id,
                    _campaign_status(snapshot, campaign_findings),
                    str(severity_counts[AnomalySeverity.CRITICAL]),
                    str(severity_counts[AnomalySeverity.WARNING]),
                    str(severity_counts[AnomalySeverity.INFO]),
                    _format_bool(
                        snapshot.requires_human_review
                        or any(finding.requires_human_review for finding in campaign_findings)
                    ),
                ]
            )

        if not rows:
            rows.append(["none", "no_campaigns", "0", "0", "0", "no"])

        return "\n".join(
            [
                heading(2, "Campaign Health Overview"),
                table(
                    [
                        "Campaign ID",
                        "Status",
                        "Critical",
                        "Warning",
                        "Info",
                        "Human Review",
                    ],
                    rows,
                ),
            ]
        )

    def _render_findings_section(
        self,
        title: str,
        findings: Sequence[AnomalyFinding],
        severity: AnomalySeverity,
    ) -> str:
        matching_findings = [finding for finding in findings if finding.severity == severity]
        lines = [heading(2, title)]
        if not matching_findings:
            lines.append(bullet(f"No {severity.value} anomalies detected."))
            return "\n".join(lines)

        lines.extend(_render_finding(finding) for finding in matching_findings)
        return "\n".join(lines)

    def _render_data_quality(
        self,
        snapshots: Sequence[CampaignSnapshot],
        findings: Sequence[AnomalyFinding],
    ) -> str:
        data_quality_findings = [
            finding for finding in findings if finding.anomaly_type in DATA_QUALITY_ANOMALY_TYPES
        ]
        lines = [heading(2, "Data Quality Issues")]

        snapshots_with_quality_issues = [
            snapshot
            for snapshot in snapshots
            if snapshot.data_quality_flags or snapshot.data_quality_notes
        ]
        if not snapshots_with_quality_issues and not data_quality_findings:
            lines.append(bullet("No data quality issues detected."))
            return "\n".join(lines)

        for snapshot in snapshots_with_quality_issues:
            flags = _format_flags(snapshot.data_quality_flags)
            notes = (
                " | ".join(snapshot.data_quality_notes)
                if snapshot.data_quality_notes
                else "none"
            )
            lines.append(
                bullet(
                    f"`{snapshot.campaign_id}`: flags={flags}; notes={_escape_inline(notes)}."
                )
            )

        for finding in data_quality_findings:
            lines.append(
                bullet(
                    f"`{finding.campaign_id}` {finding.anomaly_type.value}: "
                    f"{_escape_inline(finding.message)}"
                )
            )
        return "\n".join(lines)

    def _render_human_review(
        self,
        snapshots: Sequence[CampaignSnapshot],
        findings: Sequence[AnomalyFinding],
    ) -> str:
        review_campaign_ids = sorted(_campaign_ids_requiring_review(snapshots, findings))
        lines = [heading(2, "Human Review Required")]
        if not review_campaign_ids:
            lines.append(bullet("No campaigns require human review."))
            return "\n".join(lines)

        for campaign_id in review_campaign_ids:
            reasons = _human_review_reasons(campaign_id, snapshots, findings)
            lines.append(bullet(f"`{campaign_id}`: {'; '.join(reasons)}."))
        return "\n".join(lines)

    def _render_snapshot_table(self, snapshots: Sequence[CampaignSnapshot]) -> str:
        rows = [
            [
                snapshot.campaign_id,
                snapshot.scraped_row.name,
                snapshot.scraped_row.channel.value,
                _format_number(snapshot.scraped_row.cost),
                str(snapshot.scraped_row.conversions),
                _format_number(snapshot.scraped_row.revenue),
                _format_optional_number(
                    None
                    if snapshot.campaign_metadata is None
                    else snapshot.campaign_metadata.metrics.spend
                ),
                _format_optional_number(
                    None if snapshot.analytics_metrics is None else snapshot.analytics_metrics.cost
                ),
                _format_flags(snapshot.data_quality_flags),
                _format_bool(snapshot.requires_human_review),
            ]
            for snapshot in snapshots
        ]
        if not rows:
            rows.append(
                [
                    "none",
                    "missing",
                    "missing",
                    "missing",
                    "missing",
                    "missing",
                    "missing",
                    "missing",
                    "none",
                    "no",
                ]
            )

        return "\n".join(
            [
                heading(2, "Campaign Snapshot Table"),
                table(
                    [
                        "Campaign ID",
                        "Name",
                        "Channel",
                        "Panel Spend",
                        "Panel Conversions",
                        "Panel Revenue",
                        "Campaign API Spend",
                        "Analytics Cost",
                        "Quality Flags",
                        "Human Review",
                    ],
                    rows,
                ),
            ]
        )

    def _render_recommended_actions(self, findings: Sequence[AnomalyFinding]) -> str:
        lines = [heading(2, "Deterministic Recommended Actions")]
        if not findings:
            lines.append(bullet("No deterministic action required; continue monitoring."))
            return "\n".join(lines)

        seen_actions: set[tuple[str, str]] = set()
        for finding in findings:
            action = _action_for_finding(finding)
            action_key = (finding.campaign_id, action)
            if action_key in seen_actions:
                continue
            seen_actions.add(action_key)
            lines.append(bullet(f"`{finding.campaign_id}`: {action}"))
        return "\n".join(lines)

    def _render_limitations(self, snapshots: Sequence[CampaignSnapshot]) -> str:
        missing_metadata = [
            snapshot.campaign_id for snapshot in snapshots if snapshot.campaign_metadata is None
        ]
        missing_analytics = [
            snapshot.campaign_id for snapshot in snapshots if snapshot.analytics_metrics is None
        ]

        lines = [
            heading(2, "Limitations / Missing Data"),
            bullet(
                "Report content is limited to CampaignSnapshot and AnomalyFinding inputs; "
                "raw scraped rows, raw REST responses and raw GraphQL responses are not consumed."
            ),
            bullet("LLM interpretation is not included in this deterministic report."),
            bullet("Unavailable metrics are shown as `missing` and are not inferred."),
        ]
        lines.append(
            bullet(
                "Missing campaign metadata: "
                f"{_format_campaign_list(missing_metadata)}."
            )
        )
        lines.append(
            bullet(
                "Missing analytics metrics: "
                f"{_format_campaign_list(missing_analytics)}."
            )
        )
        return "\n".join(lines)


def generate_markdown_report(
    snapshots: Sequence[CampaignSnapshot],
    findings: Sequence[AnomalyFinding],
    metadata: ReportMetadata | None = None,
) -> str:
    """Convenience API for one-shot deterministic Markdown rendering."""

    return MarkdownReportWriter().write(snapshots, findings, metadata)


def sort_findings(findings: Sequence[AnomalyFinding]) -> list[AnomalyFinding]:
    """Return findings ordered by severity, campaign ID, type and message."""

    return sorted(
        findings,
        key=lambda finding: (
            SEVERITY_ORDER[finding.severity],
            finding.campaign_id,
            finding.anomaly_type.value,
            finding.message,
            finding.source,
        ),
    )


def findings_for_campaign(
    findings: Sequence[AnomalyFinding],
    campaign_id: str,
) -> list[AnomalyFinding]:
    """Return already sorted findings for one campaign."""

    return [finding for finding in sort_findings(findings) if finding.campaign_id == campaign_id]


def _is_healthy_campaign(
    snapshot: CampaignSnapshot,
    campaign_findings: Sequence[AnomalyFinding],
) -> bool:
    return (
        not campaign_findings
        and not snapshot.data_quality_flags
        and not snapshot.requires_human_review
    )


def _campaign_status(
    snapshot: CampaignSnapshot,
    campaign_findings: Sequence[AnomalyFinding],
) -> str:
    if snapshot.requires_human_review or any(
        finding.requires_human_review for finding in campaign_findings
    ):
        return "human_review_required"
    if any(finding.severity == AnomalySeverity.CRITICAL for finding in campaign_findings):
        return "critical"
    if any(finding.severity == AnomalySeverity.WARNING for finding in campaign_findings):
        return "warning"
    if campaign_findings:
        return "info"
    if snapshot.data_quality_flags:
        return "data_quality_issue"
    return "healthy"


def _render_finding(finding: AnomalyFinding) -> str:
    evidence = _format_evidence(finding)
    review = "yes" if finding.requires_human_review else "no"
    return bullet(
        f"`{finding.campaign_id}` {finding.anomaly_type.value} "
        f"(source: `{finding.source}`, human review: {review}): "
        f"{_escape_inline(finding.message)} Evidence: {evidence}."
    )


def _format_evidence(finding: AnomalyFinding) -> str:
    if not finding.source_evidence:
        return "none"
    return "; ".join(
        f"{key}={_format_evidence_value(value)}"
        for key, value in sorted(finding.source_evidence.items())
    )


def _format_evidence_value(value: str | int | float | bool | None) -> str:
    if value is None:
        return "missing"
    if isinstance(value, bool):
        return _format_bool(value)
    if isinstance(value, float):
        return _format_number(value)
    return _escape_inline(str(value))


def _campaign_ids_requiring_review(
    snapshots: Sequence[CampaignSnapshot],
    findings: Sequence[AnomalyFinding],
) -> set[str]:
    campaign_ids = {
        snapshot.campaign_id for snapshot in snapshots if snapshot.requires_human_review
    }
    campaign_ids.update(
        finding.campaign_id for finding in findings if finding.requires_human_review
    )
    return campaign_ids


def _human_review_reasons(
    campaign_id: str,
    snapshots: Sequence[CampaignSnapshot],
    findings: Sequence[AnomalyFinding],
) -> list[str]:
    reasons: list[str] = []
    for snapshot in snapshots:
        if snapshot.campaign_id == campaign_id and snapshot.requires_human_review:
            reasons.append("snapshot requires human review")
    reasons.extend(
        finding.anomaly_type.value
        for finding in sort_findings(findings)
        if finding.campaign_id == campaign_id and finding.requires_human_review
    )
    return reasons or ["manual review requested"]


def _action_for_finding(finding: AnomalyFinding) -> str:
    if finding.requires_human_review:
        return "pause automated follow-up until a human reviews the cited evidence."
    if finding.anomaly_type is AnomalyType.CPA_ABOVE_THRESHOLD:
        return "review targeting, creative and landing-page performance before changing spend."
    if finding.anomaly_type in {
        AnomalyType.MISSING_CAMPAIGN_METADATA,
        AnomalyType.MISSING_ANALYTICS_METRICS,
    }:
        return "repair missing source data and rerun deterministic aggregation."
    if finding.anomaly_type in {
        AnomalyType.SPEND_MISMATCH,
        AnomalyType.CONVERSIONS_MISMATCH,
        AnomalyType.REVENUE_MISMATCH,
    }:
        return "reconcile source-system metrics before making budget or task decisions."
    if finding.anomaly_type is AnomalyType.STALE_DATA:
        return "refresh campaign metadata before downstream reporting or action."
    return "review the deterministic finding and continue monitoring."


def _format_flags(flags: Sequence[DataQualityFlag]) -> str:
    if not flags:
        return "none"
    return ", ".join(flag.value for flag in flags)


def _format_campaign_list(campaign_ids: Sequence[str]) -> str:
    if not campaign_ids:
        return "none"
    return ", ".join(f"`{campaign_id}`" for campaign_id in sorted(campaign_ids))


def _format_optional_number(value: float | None) -> str:
    if value is None:
        return "missing"
    return _format_number(value)


def _format_number(value: float) -> str:
    return f"{value:.2f}"


def _format_bool(value: bool) -> str:
    return "yes" if value else "no"


def _escape_inline(value: str) -> str:
    return value.replace("`", "'").replace("\n", " ")
