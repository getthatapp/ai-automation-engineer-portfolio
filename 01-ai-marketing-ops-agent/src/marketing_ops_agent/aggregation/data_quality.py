"""Data quality flags for deterministic campaign aggregation."""

from enum import StrEnum


class DataQualityFlag(StrEnum):
    """Explicit quality markers attached to campaign snapshots."""

    MISSING_CAMPAIGN_METADATA = "missing_campaign_metadata"
    MISSING_ANALYTICS_METRICS = "missing_analytics_metrics"
    SPEND_MISMATCH = "spend_mismatch"
    CONVERSIONS_MISMATCH = "conversions_mismatch"
    REVENUE_MISMATCH = "revenue_mismatch"
    STALE_DATA = "stale_data"
    REQUIRES_HUMAN_REVIEW = "requires_human_review"


HUMAN_REVIEW_FLAGS: frozenset[DataQualityFlag] = frozenset(
    {
        DataQualityFlag.MISSING_CAMPAIGN_METADATA,
        DataQualityFlag.MISSING_ANALYTICS_METRICS,
        DataQualityFlag.SPEND_MISMATCH,
        DataQualityFlag.CONVERSIONS_MISMATCH,
        DataQualityFlag.REVENUE_MISMATCH,
        DataQualityFlag.STALE_DATA,
        DataQualityFlag.REQUIRES_HUMAN_REVIEW,
    }
)


def requires_human_review(flags: tuple[DataQualityFlag, ...]) -> bool:
    """Return whether any quality flag should block automated action."""

    return any(flag in HUMAN_REVIEW_FLAGS for flag in flags)
