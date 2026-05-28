"""Pure deterministic anomaly rules and calculations."""

from pydantic import BaseModel, ConfigDict, Field

from marketing_ops_agent.aggregation.campaign_snapshot import CampaignSnapshot
from marketing_ops_agent.aggregation.data_quality import DataQualityFlag
from marketing_ops_agent.anomaly.models import (
    AnomalySeverity,
    AnomalyType,
    SourceEvidenceValue,
)


class AnomalyThresholds(BaseModel):
    """Configurable thresholds for deterministic campaign anomaly detection."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    max_cpa: float = Field(default=50.0, gt=0)
    min_roi: float = 0.0
    high_spend_threshold: float = Field(default=10_000.0, ge=0)
    low_conversion_threshold: int = Field(default=10, ge=0)


DATA_QUALITY_FLAG_ANOMALIES: dict[
    DataQualityFlag, tuple[AnomalyType, AnomalySeverity, str]
] = {
    DataQualityFlag.MISSING_CAMPAIGN_METADATA: (
        AnomalyType.MISSING_CAMPAIGN_METADATA,
        AnomalySeverity.WARNING,
        "Campaign metadata is missing from the Campaign REST API.",
    ),
    DataQualityFlag.MISSING_ANALYTICS_METRICS: (
        AnomalyType.MISSING_ANALYTICS_METRICS,
        AnomalySeverity.WARNING,
        "Analytics metrics are missing from the Analytics GraphQL API.",
    ),
    DataQualityFlag.SPEND_MISMATCH: (
        AnomalyType.SPEND_MISMATCH,
        AnomalySeverity.WARNING,
        "Spend differs between available source systems.",
    ),
    DataQualityFlag.CONVERSIONS_MISMATCH: (
        AnomalyType.CONVERSIONS_MISMATCH,
        AnomalySeverity.CRITICAL,
        "Conversions differ between available source systems.",
    ),
    DataQualityFlag.REVENUE_MISMATCH: (
        AnomalyType.REVENUE_MISMATCH,
        AnomalySeverity.CRITICAL,
        "Revenue differs between available source systems.",
    ),
    DataQualityFlag.STALE_DATA: (
        AnomalyType.STALE_DATA,
        AnomalySeverity.WARNING,
        "Campaign metadata is stale.",
    ),
    DataQualityFlag.REQUIRES_HUMAN_REVIEW: (
        AnomalyType.REQUIRES_HUMAN_REVIEW,
        AnomalySeverity.CRITICAL,
        "Snapshot requires human review before automated follow-up actions.",
    ),
}


def calculate_cpa(*, spend: float, conversions: int) -> float | None:
    """Return cost per acquisition when conversion data permits it."""

    if conversions <= 0:
        return None
    return spend / conversions


def calculate_roi(*, revenue: float, spend: float) -> float | None:
    """Return net return on spend: (revenue - spend) / spend."""

    if spend <= 0:
        return None
    return (revenue - spend) / spend


def build_source_evidence(snapshot: CampaignSnapshot) -> dict[str, SourceEvidenceValue]:
    """Build compact source evidence without inventing missing source values."""

    evidence: dict[str, SourceEvidenceValue] = {
        "panel_campaign_id": snapshot.scraped_row.campaign_id,
        "panel_spend": snapshot.scraped_row.cost,
        "panel_conversions": snapshot.scraped_row.conversions,
        "panel_revenue": snapshot.scraped_row.revenue,
    }

    if snapshot.campaign_metadata is not None:
        evidence.update(
            {
                "campaign_api_campaign_id": snapshot.campaign_metadata.campaign_id,
                "campaign_api_spend": snapshot.campaign_metadata.metrics.spend,
                "campaign_api_conversions": snapshot.campaign_metadata.metrics.conversions,
                "campaign_api_revenue": snapshot.campaign_metadata.metrics.revenue,
                "campaign_api_collected_at": snapshot.campaign_metadata.collected_at.isoformat(),
            }
        )

    if snapshot.analytics_metrics is not None:
        evidence.update(
            {
                "analytics_campaign_id": snapshot.analytics_metrics.campaign_id,
                "analytics_cost": snapshot.analytics_metrics.cost,
                "analytics_conversions": snapshot.analytics_metrics.conversions,
                "analytics_revenue": snapshot.analytics_metrics.revenue,
            }
        )

    if snapshot.data_quality_flags:
        evidence["data_quality_flags"] = ",".join(
            flag.value for flag in snapshot.data_quality_flags
        )

    if snapshot.data_quality_notes:
        evidence["data_quality_notes"] = " | ".join(snapshot.data_quality_notes)

    return evidence
