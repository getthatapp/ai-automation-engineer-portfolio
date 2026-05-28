"""Typed anomaly models for deterministic campaign analysis."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AnomalySeverity(StrEnum):
    """Business severity for deterministic anomaly findings."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AnomalyType(StrEnum):
    """Supported deterministic anomaly categories."""

    HIGH_SPEND_LOW_CONVERSIONS = "high_spend_low_conversions"
    CPA_ABOVE_THRESHOLD = "cpa_above_threshold"
    NEGATIVE_ROI = "negative_roi"
    MISSING_CAMPAIGN_METADATA = "missing_campaign_metadata"
    MISSING_ANALYTICS_METRICS = "missing_analytics_metrics"
    SPEND_MISMATCH = "spend_mismatch"
    CONVERSIONS_MISMATCH = "conversions_mismatch"
    REVENUE_MISMATCH = "revenue_mismatch"
    STALE_DATA = "stale_data"
    REQUIRES_HUMAN_REVIEW = "requires_human_review"


SourceEvidenceValue = str | int | float | bool | None


class AnomalyFinding(BaseModel):
    """A deterministic finding emitted from an aggregated campaign snapshot."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    campaign_id: str = Field(min_length=1)
    anomaly_type: AnomalyType
    severity: AnomalySeverity
    message: str = Field(min_length=1)
    source: str = Field(min_length=1)
    source_evidence: dict[str, SourceEvidenceValue] = Field(default_factory=dict)
    requires_human_review: bool = False

    @field_validator("campaign_id", "message", "source")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        """Trim required text fields and reject blank values.

        Args:
            value: Raw field value.

        Returns:
            Stripped non-empty value.

        Raises:
            ValueError: If the stripped value is blank.
        """
        stripped = value.strip()
        if not stripped:
            raise ValueError("value must not be blank")
        return stripped
