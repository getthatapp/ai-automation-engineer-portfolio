from datetime import UTC, datetime

from marketing_ops_agent.aggregation.campaign_snapshot import CampaignSnapshot
from marketing_ops_agent.aggregation.data_quality import DataQualityFlag
from marketing_ops_agent.anomaly import (
    AnomalyDetector,
    AnomalyFinding,
    AnomalySeverity,
    AnomalyThresholds,
    AnomalyType,
)
from marketing_ops_agent.browser.panel_scraper import ScrapedCampaignRow
from marketing_ops_agent.clients.analytics_client import AnalyticsCampaignMetrics
from marketing_ops_agent.models import Campaign, CampaignMetrics, Channel

REFERENCE_TIME = datetime(2026, 5, 28, 12, 0, tzinfo=UTC)
_DEFAULT = object()


def test_no_anomalies_on_healthy_campaign() -> None:
    findings = AnomalyDetector().detect([_snapshot()])

    assert findings == []


def test_detects_high_spend_and_low_conversions() -> None:
    snapshot = _snapshot(row=_row(conversions=2, cost=12_000.0, revenue=18_000.0))

    findings = AnomalyDetector().detect([snapshot])

    finding = _single_finding(findings, AnomalyType.HIGH_SPEND_LOW_CONVERSIONS)
    assert finding.severity is AnomalySeverity.CRITICAL
    assert finding.requires_human_review is True
    assert finding.source_evidence["panel_spend"] == 12_000.0
    assert finding.source_evidence["panel_conversions"] == 2


def test_detects_cpa_above_threshold() -> None:
    snapshot = _snapshot(row=_row(conversions=100, cost=7_500.0, revenue=20_000.0))

    findings = AnomalyDetector().detect([snapshot])

    finding = _single_finding(findings, AnomalyType.CPA_ABOVE_THRESHOLD)
    assert finding.severity is AnomalySeverity.WARNING
    assert finding.source_evidence["panel_cpa"] == 75.0
    assert finding.source_evidence["max_cpa"] == 50.0


def test_detects_negative_roi() -> None:
    snapshot = _snapshot(row=_row(cost=10_000.0, revenue=8_000.0))

    findings = AnomalyDetector().detect([snapshot])

    finding = _single_finding(findings, AnomalyType.NEGATIVE_ROI)
    assert finding.severity is AnomalySeverity.CRITICAL
    assert finding.requires_human_review is True
    assert finding.source_evidence["panel_roi"] == -0.2


def test_maps_missing_metadata_flag() -> None:
    snapshot = _snapshot(
        campaign_metadata=None,
        flags=(DataQualityFlag.MISSING_CAMPAIGN_METADATA,),
        requires_human_review=True,
    )

    findings = AnomalyDetector().detect([snapshot])

    missing_metadata = _single_finding(findings, AnomalyType.MISSING_CAMPAIGN_METADATA)
    requires_review = _single_finding(findings, AnomalyType.REQUIRES_HUMAN_REVIEW)
    assert missing_metadata.severity is AnomalySeverity.WARNING
    assert missing_metadata.source == "aggregation_data_quality"
    assert "campaign_api_spend" not in missing_metadata.source_evidence
    assert requires_review.severity is AnomalySeverity.CRITICAL


def test_maps_missing_analytics_flag() -> None:
    snapshot = _snapshot(
        analytics_metrics=None,
        flags=(DataQualityFlag.MISSING_ANALYTICS_METRICS,),
        requires_human_review=True,
    )

    findings = AnomalyDetector().detect([snapshot])

    finding = _single_finding(findings, AnomalyType.MISSING_ANALYTICS_METRICS)
    assert finding.severity is AnomalySeverity.WARNING
    assert "analytics_cost" not in finding.source_evidence


def test_maps_mismatch_flags() -> None:
    snapshot = _snapshot(
        flags=(
            DataQualityFlag.SPEND_MISMATCH,
            DataQualityFlag.CONVERSIONS_MISMATCH,
            DataQualityFlag.REVENUE_MISMATCH,
        ),
        requires_human_review=True,
    )

    findings = AnomalyDetector().detect([snapshot])
    finding_types = {finding.anomaly_type for finding in findings}

    assert AnomalyType.SPEND_MISMATCH in finding_types
    assert AnomalyType.CONVERSIONS_MISMATCH in finding_types
    assert AnomalyType.REVENUE_MISMATCH in finding_types
    assert _single_finding(findings, AnomalyType.SPEND_MISMATCH).severity is (
        AnomalySeverity.WARNING
    )
    assert _single_finding(findings, AnomalyType.CONVERSIONS_MISMATCH).severity is (
        AnomalySeverity.CRITICAL
    )


def test_maps_stale_data_flag() -> None:
    snapshot = _snapshot(
        flags=(DataQualityFlag.STALE_DATA,),
        requires_human_review=True,
    )

    findings = AnomalyDetector().detect([snapshot])

    finding = _single_finding(findings, AnomalyType.STALE_DATA)
    assert finding.severity is AnomalySeverity.WARNING
    assert finding.source_evidence["data_quality_flag"] == "stale_data"


def test_maps_requires_human_review_flag_as_critical() -> None:
    snapshot = _snapshot(
        flags=(DataQualityFlag.REQUIRES_HUMAN_REVIEW,),
        requires_human_review=True,
    )

    findings = AnomalyDetector().detect([snapshot])

    finding = _single_finding(findings, AnomalyType.REQUIRES_HUMAN_REVIEW)
    assert finding.severity is AnomalySeverity.CRITICAL
    assert finding.requires_human_review is True


def test_detects_multiple_anomalies_for_one_campaign() -> None:
    snapshot = _snapshot(
        row=_row(conversions=5, cost=12_000.0, revenue=6_000.0),
        flags=(DataQualityFlag.SPEND_MISMATCH,),
        requires_human_review=True,
    )

    findings = AnomalyDetector(
        thresholds=AnomalyThresholds(max_cpa=100.0, min_roi=0.0)
    ).detect([snapshot])
    finding_types = {finding.anomaly_type for finding in findings}

    assert finding_types == {
        AnomalyType.HIGH_SPEND_LOW_CONVERSIONS,
        AnomalyType.CPA_ABOVE_THRESHOLD,
        AnomalyType.NEGATIVE_ROI,
        AnomalyType.SPEND_MISMATCH,
        AnomalyType.REQUIRES_HUMAN_REVIEW,
    }


def _single_finding(
    findings: list[AnomalyFinding],
    anomaly_type: AnomalyType,
) -> AnomalyFinding:
    matches = [finding for finding in findings if finding.anomaly_type == anomaly_type]
    assert len(matches) == 1
    return matches[0]


def _snapshot(
    *,
    row: ScrapedCampaignRow | None = None,
    campaign_metadata: Campaign | None | object = _DEFAULT,
    analytics_metrics: AnalyticsCampaignMetrics | None | object = _DEFAULT,
    flags: tuple[DataQualityFlag, ...] = (),
    notes: tuple[str, ...] = (),
    requires_human_review: bool = False,
) -> CampaignSnapshot:
    resolved_row = row or _row()
    resolved_campaign = _campaign() if campaign_metadata is _DEFAULT else campaign_metadata
    resolved_analytics = _analytics() if analytics_metrics is _DEFAULT else analytics_metrics
    return CampaignSnapshot(
        campaign_id=resolved_row.campaign_id,
        scraped_row=resolved_row,
        campaign_metadata=resolved_campaign,
        analytics_metrics=resolved_analytics,
        data_quality_flags=flags,
        data_quality_notes=notes,
        requires_human_review=requires_human_review,
        aggregated_at=REFERENCE_TIME,
    )


def _row(
    *,
    conversions: int = 640,
    cost: float = 12_150.0,
    revenue: float = 38_400.0,
) -> ScrapedCampaignRow:
    return ScrapedCampaignRow(
        campaign_id="cmp-search-brand",
        name="Brand Search Defense",
        channel=Channel.SEARCH,
        impressions=120_000,
        clicks=8_200,
        conversions=conversions,
        cost=cost,
        revenue=revenue,
    )


def _campaign() -> Campaign:
    return Campaign(
        campaign_id="cmp-search-brand",
        name="Brand Search Defense",
        channel=Channel.SEARCH,
        metrics=CampaignMetrics(
            impressions=120_000,
            clicks=8_200,
            conversions=640,
            spend=12_150.0,
            revenue=38_400.0,
        ),
        collected_at=datetime(2026, 5, 28, 8, 0, tzinfo=UTC),
    )


def _analytics() -> AnalyticsCampaignMetrics:
    return AnalyticsCampaignMetrics(
        campaignId="cmp-search-brand",
        impressions=120_000,
        clicks=8_200,
        conversions=640,
        revenue=38_400.0,
        cost=12_150.0,
    )
