"""Deterministic anomaly detector for aggregated campaign snapshots."""

from collections.abc import Sequence

from marketing_ops_agent.aggregation.campaign_snapshot import CampaignSnapshot
from marketing_ops_agent.aggregation.data_quality import DataQualityFlag
from marketing_ops_agent.anomaly.models import (
    AnomalyFinding,
    AnomalySeverity,
    AnomalyType,
    SourceEvidenceValue,
)
from marketing_ops_agent.anomaly.rules import (
    DATA_QUALITY_FLAG_ANOMALIES,
    AnomalyThresholds,
    build_source_evidence,
    calculate_cpa,
    calculate_roi,
)


class AnomalyDetector:
    """Evaluate campaign snapshots using deterministic business rules."""

    def __init__(self, thresholds: AnomalyThresholds | None = None) -> None:
        """Initialize the detector with explicit or default thresholds.

        Args:
            thresholds: Optional deterministic anomaly thresholds.
        """
        self._thresholds = thresholds or AnomalyThresholds()

    def detect(self, snapshots: Sequence[CampaignSnapshot]) -> list[AnomalyFinding]:
        """Return anomaly findings for the provided campaign snapshots."""

        findings: list[AnomalyFinding] = []
        for snapshot in snapshots:
            findings.extend(self._detect_for_snapshot(snapshot))
        return findings

    def _detect_for_snapshot(self, snapshot: CampaignSnapshot) -> list[AnomalyFinding]:
        """Evaluate performance and data quality rules for one snapshot.

        Args:
            snapshot: Aggregated campaign snapshot to evaluate.

        Returns:
            Deterministic anomaly findings for the campaign.
        """
        findings: list[AnomalyFinding] = []
        evidence = build_source_evidence(snapshot)
        row = snapshot.scraped_row
        cpa = calculate_cpa(spend=row.cost, conversions=row.conversions)
        roi = calculate_roi(revenue=row.revenue, spend=row.cost)

        if cpa is not None:
            evidence["panel_cpa"] = cpa
        if roi is not None:
            evidence["panel_roi"] = roi

        if (
            row.cost >= self._thresholds.high_spend_threshold
            and row.conversions <= self._thresholds.low_conversion_threshold
        ):
            findings.append(
                AnomalyFinding(
                    campaign_id=snapshot.campaign_id,
                    anomaly_type=AnomalyType.HIGH_SPEND_LOW_CONVERSIONS,
                    severity=AnomalySeverity.CRITICAL,
                    message=(
                        "Campaign spend is high while conversions are at or below "
                        "the low-conversion threshold."
                    ),
                    source="marketing_panel",
                    source_evidence={
                        **evidence,
                        "high_spend_threshold": self._thresholds.high_spend_threshold,
                        "low_conversion_threshold": self._thresholds.low_conversion_threshold,
                    },
                    requires_human_review=True,
                )
            )

        if cpa is not None and cpa > self._thresholds.max_cpa:
            findings.append(
                AnomalyFinding(
                    campaign_id=snapshot.campaign_id,
                    anomaly_type=AnomalyType.CPA_ABOVE_THRESHOLD,
                    severity=AnomalySeverity.WARNING,
                    message="Campaign CPA is above the configured threshold.",
                    source="marketing_panel",
                    source_evidence={
                        **evidence,
                        "max_cpa": self._thresholds.max_cpa,
                    },
                    requires_human_review=False,
                )
            )

        if roi is not None and roi < self._thresholds.min_roi:
            findings.append(
                AnomalyFinding(
                    campaign_id=snapshot.campaign_id,
                    anomaly_type=AnomalyType.NEGATIVE_ROI,
                    severity=AnomalySeverity.CRITICAL,
                    message="Campaign ROI is below the configured minimum threshold.",
                    source="marketing_panel",
                    source_evidence={
                        **evidence,
                        "min_roi": self._thresholds.min_roi,
                    },
                    requires_human_review=True,
                )
            )

        findings.extend(self._map_data_quality_flags(snapshot, evidence))
        return findings

    def _map_data_quality_flags(
        self,
        snapshot: CampaignSnapshot,
        evidence: dict[str, SourceEvidenceValue],
    ) -> list[AnomalyFinding]:
        """Convert data quality flags into anomaly findings.

        Args:
            snapshot: Aggregated campaign snapshot with quality flags.
            evidence: Source evidence already collected for the snapshot.

        Returns:
            Findings that preserve data quality flags and review requirements.
        """
        findings: list[AnomalyFinding] = []

        for flag in snapshot.data_quality_flags:
            anomaly_config = DATA_QUALITY_FLAG_ANOMALIES.get(flag)
            if anomaly_config is None:
                continue

            anomaly_type, severity, message = anomaly_config
            findings.append(
                AnomalyFinding(
                    campaign_id=snapshot.campaign_id,
                    anomaly_type=anomaly_type,
                    severity=severity,
                    message=message,
                    source="aggregation_data_quality",
                    source_evidence={
                        **evidence,
                        "data_quality_flag": flag.value,
                    },
                    requires_human_review=(
                        severity is AnomalySeverity.CRITICAL
                        or flag is DataQualityFlag.REQUIRES_HUMAN_REVIEW
                    ),
                )
            )

        if snapshot.requires_human_review and (
            DataQualityFlag.REQUIRES_HUMAN_REVIEW not in snapshot.data_quality_flags
        ):
            findings.append(
                AnomalyFinding(
                    campaign_id=snapshot.campaign_id,
                    anomaly_type=AnomalyType.REQUIRES_HUMAN_REVIEW,
                    severity=AnomalySeverity.CRITICAL,
                    message="Snapshot requires human review before automated follow-up actions.",
                    source="aggregation_data_quality",
                    source_evidence={
                        **evidence,
                        "requires_human_review": snapshot.requires_human_review,
                    },
                    requires_human_review=True,
                )
            )

        return findings
