from datetime import UTC, datetime

from marketing_ops_agent.aggregation.campaign_snapshot import CampaignSnapshot
from marketing_ops_agent.aggregation.data_quality import DataQualityFlag
from marketing_ops_agent.anomaly import AnomalyFinding, AnomalySeverity, AnomalyType
from marketing_ops_agent.browser.panel_scraper import ScrapedCampaignRow
from marketing_ops_agent.clients.analytics_client import AnalyticsCampaignMetrics
from marketing_ops_agent.models import Campaign, CampaignMetrics, Channel
from marketing_ops_agent.reporting import (
    ReportMetadata,
    generate_markdown_report,
    sort_findings,
)

REFERENCE_TIME = datetime(2026, 5, 28, 12, 0, tzinfo=UTC)
_DEFAULT = object()


def test_report_contains_title_and_timestamp() -> None:
    report = _report([_snapshot()], [])

    assert report.startswith("# Weekly Ops Report")
    assert "Generated timestamp: 2026-05-28T12:00:00+00:00" in report


def test_healthy_campaign_summary() -> None:
    report = _report([_snapshot()], [])

    assert "## Executive Summary" in report
    assert "- Campaigns processed: 1." in report
    assert "- Healthy campaigns: 1." in report
    assert "All campaigns are healthy" in report
    assert "| cmp-search-brand | healthy | 0 | 0 | 0 | no |" in report


def test_critical_anomaly_section() -> None:
    finding = _finding(
        anomaly_type=AnomalyType.NEGATIVE_ROI,
        severity=AnomalySeverity.CRITICAL,
        message="Campaign ROI is below the configured minimum threshold.",
        requires_human_review=True,
    )

    report = _report([_snapshot()], [finding])

    assert "## Critical Anomalies" in report
    assert "`cmp-search-brand` negative_roi" in report
    assert "Campaign ROI is below the configured minimum threshold." in report
    assert "human review: yes" in report


def test_warning_anomaly_section() -> None:
    finding = _finding(
        anomaly_type=AnomalyType.CPA_ABOVE_THRESHOLD,
        severity=AnomalySeverity.WARNING,
        message="Campaign CPA is above the configured threshold.",
    )

    report = _report([_snapshot()], [finding])

    assert "## Warning Anomalies" in report
    assert "`cmp-search-brand` cpa_above_threshold" in report
    assert "Campaign CPA is above the configured threshold." in report


def test_data_quality_section() -> None:
    snapshot = _snapshot(
        flags=(DataQualityFlag.MISSING_CAMPAIGN_METADATA,),
        notes=("Campaign API returned 404.",),
        campaign_metadata=None,
        requires_human_review=True,
    )
    finding = _finding(
        anomaly_type=AnomalyType.MISSING_CAMPAIGN_METADATA,
        severity=AnomalySeverity.WARNING,
        message="Campaign metadata is missing from the Campaign REST API.",
        source="aggregation_data_quality",
    )

    report = _report([snapshot], [finding])

    assert "## Data Quality Issues" in report
    assert "flags=missing_campaign_metadata" in report
    assert "Campaign API returned 404." in report
    assert "`cmp-search-brand` missing_campaign_metadata" in report


def test_human_review_section() -> None:
    snapshot = _snapshot(requires_human_review=True)
    finding = _finding(
        anomaly_type=AnomalyType.HIGH_SPEND_LOW_CONVERSIONS,
        severity=AnomalySeverity.CRITICAL,
        message="High spend with low conversions.",
        requires_human_review=True,
    )

    report = _report([snapshot], [finding])

    assert "## Human Review Required" in report
    assert (
        "`cmp-search-brand`: snapshot requires human review; high_spend_low_conversions."
        in report
    )


def test_campaign_snapshot_table() -> None:
    report = _report([_snapshot()], [])

    assert "## Campaign Snapshot Table" in report
    assert (
        "| Campaign ID | Name | Channel | Panel Spend | Panel Conversions | Panel Revenue | "
        "Campaign API Spend | Analytics Cost | Quality Flags | Human Review |"
    ) in report
    assert (
        "| cmp-search-brand | Brand Search Defense | search | 12150.00 | 640 | 38400.00 | "
        "12150.00 | 12150.00 | none | no |"
    ) in report


def test_missing_data_is_explicitly_shown() -> None:
    snapshot = _snapshot(
        campaign_id="cmp-missing",
        name="Missing Data Campaign",
        channel=Channel.SOCIAL,
        campaign_metadata=None,
        analytics_metrics=None,
        flags=(
            DataQualityFlag.MISSING_CAMPAIGN_METADATA,
            DataQualityFlag.MISSING_ANALYTICS_METRICS,
        ),
        requires_human_review=True,
    )

    report = _report([snapshot], [])

    assert (
        "| cmp-missing | Missing Data Campaign | social | 12150.00 | 640 | 38400.00 | "
        "missing | missing | missing_campaign_metadata, missing_analytics_metrics | yes |"
    ) in report
    assert "Missing campaign metadata: `cmp-missing`." in report
    assert "Missing analytics metrics: `cmp-missing`." in report


def test_report_does_not_invent_unavailable_metrics() -> None:
    snapshot = _snapshot(
        campaign_metadata=None,
        analytics_metrics=None,
        flags=(
            DataQualityFlag.MISSING_CAMPAIGN_METADATA,
            DataQualityFlag.MISSING_ANALYTICS_METRICS,
        ),
        requires_human_review=True,
    )

    report = _report([snapshot], [])

    assert "Campaign API Spend | Analytics Cost" in report
    assert "missing | missing" in report
    assert "campaign_api_spend=" not in report
    assert "analytics_cost=" not in report
    assert "Unavailable metrics are shown as `missing` and are not inferred." in report


def test_stable_ordering_of_findings() -> None:
    warning = _finding(
        campaign_id="cmp-b",
        anomaly_type=AnomalyType.CPA_ABOVE_THRESHOLD,
        severity=AnomalySeverity.WARNING,
        message="Warning B.",
    )
    critical_z = _finding(
        campaign_id="cmp-z",
        anomaly_type=AnomalyType.NEGATIVE_ROI,
        severity=AnomalySeverity.CRITICAL,
        message="Critical Z.",
    )
    info = _finding(
        campaign_id="cmp-a",
        anomaly_type=AnomalyType.STALE_DATA,
        severity=AnomalySeverity.INFO,
        message="Info A.",
    )
    critical_a = _finding(
        campaign_id="cmp-a",
        anomaly_type=AnomalyType.HIGH_SPEND_LOW_CONVERSIONS,
        severity=AnomalySeverity.CRITICAL,
        message="Critical A.",
    )

    sorted_findings = sort_findings([warning, critical_z, info, critical_a])

    assert sorted_findings == [critical_a, critical_z, warning, info]

    report = _report(
        [
            _snapshot(campaign_id="cmp-a"),
            _snapshot(campaign_id="cmp-b"),
            _snapshot(campaign_id="cmp-z"),
        ],
        [warning, critical_z, info, critical_a],
    )
    assert report.index("`cmp-a` high_spend_low_conversions") < report.index("`cmp-z` negative_roi")
    assert report.index("`cmp-z` negative_roi") < report.index("`cmp-b` cpa_above_threshold")


def _report(
    snapshots: list[CampaignSnapshot],
    findings: list[AnomalyFinding],
) -> str:
    return generate_markdown_report(
        snapshots,
        findings,
        ReportMetadata(title="Weekly Ops Report", generated_at=REFERENCE_TIME),
    )


def _snapshot(
    *,
    campaign_id: str = "cmp-search-brand",
    name: str = "Brand Search Defense",
    channel: Channel = Channel.SEARCH,
    campaign_metadata: Campaign | None | object = _DEFAULT,
    analytics_metrics: AnalyticsCampaignMetrics | None | object = _DEFAULT,
    flags: tuple[DataQualityFlag, ...] = (),
    notes: tuple[str, ...] = (),
    requires_human_review: bool = False,
) -> CampaignSnapshot:
    row = _row(campaign_id=campaign_id, name=name, channel=channel)
    resolved_campaign = (
        _campaign(campaign_id=campaign_id, name=name, channel=channel)
        if campaign_metadata is _DEFAULT
        else campaign_metadata
    )
    resolved_analytics = (
        _analytics(campaign_id=campaign_id) if analytics_metrics is _DEFAULT else analytics_metrics
    )
    return CampaignSnapshot(
        campaign_id=campaign_id,
        scraped_row=row,
        campaign_metadata=resolved_campaign,
        analytics_metrics=resolved_analytics,
        data_quality_flags=flags,
        data_quality_notes=notes,
        requires_human_review=requires_human_review,
        aggregated_at=REFERENCE_TIME,
    )


def _row(
    *,
    campaign_id: str,
    name: str,
    channel: Channel,
) -> ScrapedCampaignRow:
    return ScrapedCampaignRow(
        campaign_id=campaign_id,
        name=name,
        channel=channel,
        impressions=120_000,
        clicks=8_200,
        conversions=640,
        cost=12_150.0,
        revenue=38_400.0,
    )


def _campaign(
    *,
    campaign_id: str,
    name: str,
    channel: Channel,
) -> Campaign:
    return Campaign(
        campaign_id=campaign_id,
        name=name,
        channel=channel,
        metrics=CampaignMetrics(
            impressions=120_000,
            clicks=8_200,
            conversions=640,
            spend=12_150.0,
            revenue=38_400.0,
        ),
        collected_at=REFERENCE_TIME,
    )


def _analytics(*, campaign_id: str) -> AnalyticsCampaignMetrics:
    return AnalyticsCampaignMetrics(
        campaignId=campaign_id,
        impressions=120_000,
        clicks=8_200,
        conversions=640,
        revenue=38_400.0,
        cost=12_150.0,
    )


def _finding(
    *,
    campaign_id: str = "cmp-search-brand",
    anomaly_type: AnomalyType,
    severity: AnomalySeverity,
    message: str,
    source: str = "marketing_panel",
    requires_human_review: bool = False,
) -> AnomalyFinding:
    return AnomalyFinding(
        campaign_id=campaign_id,
        anomaly_type=anomaly_type,
        severity=severity,
        message=message,
        source=source,
        source_evidence={
            "panel_spend": 12_150.0,
            "panel_conversions": 640,
        },
        requires_human_review=requires_human_review,
    )
