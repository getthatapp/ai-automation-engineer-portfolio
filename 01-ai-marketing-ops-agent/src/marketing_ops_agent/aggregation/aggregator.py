"""Deterministic campaign data aggregation service."""

from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from typing import Protocol

from marketing_ops_agent.aggregation.campaign_snapshot import CampaignSnapshot
from marketing_ops_agent.aggregation.data_quality import DataQualityFlag, requires_human_review
from marketing_ops_agent.aggregation.errors import DuplicateCampaignRowsError
from marketing_ops_agent.browser.panel_scraper import ScrapedCampaignRow
from marketing_ops_agent.clients.analytics_client import AnalyticsCampaignMetrics
from marketing_ops_agent.clients.errors import ServiceClientError
from marketing_ops_agent.models import Campaign


class CampaignMetadataClient(Protocol):
    """Client contract needed for campaign metadata aggregation."""

    async def get_campaign(self, campaign_id: str) -> Campaign:
        """Return campaign metadata for one campaign ID.

        Args:
            campaign_id: Campaign identifier from the scraped panel row.

        Returns:
            Validated campaign metadata from the Campaign REST API boundary.
        """
        ...


class CampaignAnalyticsClient(Protocol):
    """Client contract needed for campaign analytics aggregation."""

    async def get_campaign_metrics(self, campaign_id: str) -> AnalyticsCampaignMetrics:
        """Return analytics metrics for one campaign ID.

        Args:
            campaign_id: Campaign identifier from the scraped panel row.

        Returns:
            Validated metrics from the Analytics GraphQL boundary.
        """
        ...


class CampaignAggregator:
    """Join scraped panel rows with REST metadata and GraphQL metrics."""

    def __init__(
        self,
        *,
        campaign_client: CampaignMetadataClient,
        analytics_client: CampaignAnalyticsClient,
        stale_after: timedelta = timedelta(hours=24),
        money_tolerance: float = 0.01,
    ) -> None:
        """Initialize the aggregator with API client boundaries and tolerances.

        Args:
            campaign_client: Client used to fetch Campaign REST API metadata.
            analytics_client: Client used to fetch Analytics GraphQL metrics.
            stale_after: Maximum accepted age for campaign metadata.
            money_tolerance: Absolute tolerance when comparing money values.
        """
        self._campaign_client = campaign_client
        self._analytics_client = analytics_client
        self._stale_after = stale_after
        self._money_tolerance = money_tolerance

    async def aggregate(
        self,
        scraped_rows: Sequence[ScrapedCampaignRow],
        *,
        reference_time: datetime | None = None,
    ) -> list[CampaignSnapshot]:
        """Aggregate scraped rows into validated campaign snapshots."""

        self._validate_unique_campaign_ids(scraped_rows)
        aggregated_at = reference_time or datetime.now(UTC)

        snapshots: list[CampaignSnapshot] = []
        for row in scraped_rows:
            campaign_metadata, campaign_error = await self._fetch_campaign_metadata(
                row.campaign_id
            )
            analytics_metrics, analytics_error = await self._fetch_analytics_metrics(
                row.campaign_id
            )
            flags, notes = self._evaluate_quality(
                row=row,
                campaign_metadata=campaign_metadata,
                analytics_metrics=analytics_metrics,
                campaign_error=campaign_error,
                analytics_error=analytics_error,
                reference_time=aggregated_at,
            )

            snapshots.append(
                CampaignSnapshot(
                    campaign_id=row.campaign_id,
                    scraped_row=row,
                    campaign_metadata=campaign_metadata,
                    analytics_metrics=analytics_metrics,
                    data_quality_flags=tuple(flags),
                    data_quality_notes=tuple(notes),
                    requires_human_review=requires_human_review(tuple(flags)),
                    aggregated_at=aggregated_at,
                )
            )

        return snapshots

    async def _fetch_campaign_metadata(
        self,
        campaign_id: str,
    ) -> tuple[Campaign | None, str | None]:
        """Fetch campaign metadata while preserving service errors as notes.

        Args:
            campaign_id: Campaign identifier to request.

        Returns:
            Tuple of optional campaign metadata and optional error text.
        """
        try:
            return await self._campaign_client.get_campaign(campaign_id), None
        except ServiceClientError as exc:
            return None, str(exc)

    async def _fetch_analytics_metrics(
        self,
        campaign_id: str,
    ) -> tuple[AnalyticsCampaignMetrics | None, str | None]:
        """Fetch analytics metrics while preserving service errors as notes.

        Args:
            campaign_id: Campaign identifier to request.

        Returns:
            Tuple of optional analytics metrics and optional error text.
        """
        try:
            return await self._analytics_client.get_campaign_metrics(campaign_id), None
        except ServiceClientError as exc:
            return None, str(exc)

    def _evaluate_quality(
        self,
        *,
        row: ScrapedCampaignRow,
        campaign_metadata: Campaign | None,
        analytics_metrics: AnalyticsCampaignMetrics | None,
        campaign_error: str | None,
        analytics_error: str | None,
        reference_time: datetime,
    ) -> tuple[list[DataQualityFlag], list[str]]:
        """Evaluate missing data, staleness and metric mismatches for a row.

        Args:
            row: Validated panel row.
            campaign_metadata: Optional Campaign REST API metadata.
            analytics_metrics: Optional Analytics GraphQL metrics.
            campaign_error: Error text captured while fetching campaign metadata.
            analytics_error: Error text captured while fetching analytics metrics.
            reference_time: Timestamp used for stale data checks.

        Returns:
            Ordered data quality flags and notes for the campaign snapshot.
        """
        flags: list[DataQualityFlag] = []
        notes: list[str] = []

        if campaign_metadata is None:
            self._add_flag(
                flags,
                notes,
                DataQualityFlag.MISSING_CAMPAIGN_METADATA,
                f"Campaign REST API did not return metadata for {row.campaign_id}."
                + self._format_error_note(campaign_error),
            )
        elif self._is_stale(campaign_metadata.collected_at, reference_time):
            self._add_flag(
                flags,
                notes,
                DataQualityFlag.STALE_DATA,
                (
                    "Campaign REST API metadata is older than "
                    f"{self._stale_after.total_seconds() / 3600:g} hours."
                ),
            )

        if analytics_metrics is None:
            self._add_flag(
                flags,
                notes,
                DataQualityFlag.MISSING_ANALYTICS_METRICS,
                f"Analytics GraphQL API did not return metrics for {row.campaign_id}."
                + self._format_error_note(analytics_error),
            )

        if self._spend_mismatch(row, campaign_metadata, analytics_metrics):
            self._add_flag(
                flags,
                notes,
                DataQualityFlag.SPEND_MISMATCH,
                "Spend differs between panel, Campaign API or Analytics GraphQL.",
            )

        if self._conversions_mismatch(row, campaign_metadata, analytics_metrics):
            self._add_flag(
                flags,
                notes,
                DataQualityFlag.CONVERSIONS_MISMATCH,
                "Conversions differ between panel, Campaign API or Analytics GraphQL.",
            )

        if self._revenue_mismatch(row, campaign_metadata, analytics_metrics):
            self._add_flag(
                flags,
                notes,
                DataQualityFlag.REVENUE_MISMATCH,
                "Revenue differs between panel, Campaign API or Analytics GraphQL.",
            )

        if requires_human_review(tuple(flags)):
            self._add_flag(
                flags,
                notes,
                DataQualityFlag.REQUIRES_HUMAN_REVIEW,
                "Snapshot requires human review before automated follow-up actions.",
            )

        return flags, notes

    def _spend_mismatch(
        self,
        row: ScrapedCampaignRow,
        campaign_metadata: Campaign | None,
        analytics_metrics: AnalyticsCampaignMetrics | None,
    ) -> bool:
        """Return whether spend differs across available sources.

        Args:
            row: Validated panel row.
            campaign_metadata: Optional Campaign REST API metadata.
            analytics_metrics: Optional Analytics GraphQL metrics.

        Returns:
            True when available spend values exceed the money tolerance.
        """
        values = [row.cost]
        if campaign_metadata is not None:
            values.append(campaign_metadata.metrics.spend)
        if analytics_metrics is not None:
            values.append(analytics_metrics.cost)
        return self._money_values_mismatch(values)

    def _revenue_mismatch(
        self,
        row: ScrapedCampaignRow,
        campaign_metadata: Campaign | None,
        analytics_metrics: AnalyticsCampaignMetrics | None,
    ) -> bool:
        """Return whether revenue differs across available sources.

        Args:
            row: Validated panel row.
            campaign_metadata: Optional Campaign REST API metadata.
            analytics_metrics: Optional Analytics GraphQL metrics.

        Returns:
            True when available revenue values exceed the money tolerance.
        """
        values = [row.revenue]
        if campaign_metadata is not None:
            values.append(campaign_metadata.metrics.revenue)
        if analytics_metrics is not None:
            values.append(analytics_metrics.revenue)
        return self._money_values_mismatch(values)

    @staticmethod
    def _conversions_mismatch(
        row: ScrapedCampaignRow,
        campaign_metadata: Campaign | None,
        analytics_metrics: AnalyticsCampaignMetrics | None,
    ) -> bool:
        """Return whether conversion counts differ across available sources.

        Args:
            row: Validated panel row.
            campaign_metadata: Optional Campaign REST API metadata.
            analytics_metrics: Optional Analytics GraphQL metrics.

        Returns:
            True when available conversion values are not identical.
        """
        values = [row.conversions]
        if campaign_metadata is not None:
            values.append(campaign_metadata.metrics.conversions)
        if analytics_metrics is not None:
            values.append(analytics_metrics.conversions)
        return len(set(values)) > 1

    def _money_values_mismatch(self, values: Sequence[float]) -> bool:
        """Return whether money values exceed the configured tolerance.

        Args:
            values: Available money values from deterministic sources.

        Returns:
            True when the highest and lowest values differ beyond tolerance.
        """
        return max(values) - min(values) > self._money_tolerance

    def _is_stale(self, collected_at: datetime, reference_time: datetime) -> bool:
        """Return whether metadata is older than the configured freshness window.

        Args:
            collected_at: Source metadata collection timestamp.
            reference_time: Workflow reference timestamp.

        Returns:
            True when the normalized age exceeds `stale_after`.
        """
        normalized_collected_at = self._normalize_datetime(collected_at)
        normalized_reference_time = self._normalize_datetime(reference_time)
        return normalized_reference_time - normalized_collected_at > self._stale_after

    @staticmethod
    def _normalize_datetime(value: datetime) -> datetime:
        """Normalize a datetime to UTC, treating naive values as UTC.

        Args:
            value: Datetime to normalize.

        Returns:
            Timezone-aware UTC datetime.
        """
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)

    @staticmethod
    def _add_flag(
        flags: list[DataQualityFlag],
        notes: list[str],
        flag: DataQualityFlag,
        note: str,
    ) -> None:
        """Append a data quality flag and note once.

        Args:
            flags: Mutable ordered flag collection.
            notes: Mutable ordered note collection.
            flag: Flag to add when absent.
            note: Human-readable quality note paired with the flag.
        """
        if flag not in flags:
            flags.append(flag)
            notes.append(note)

    @staticmethod
    def _format_error_note(error: str | None) -> str:
        """Format optional service error text for a data quality note.

        Args:
            error: Optional service error text.

        Returns:
            Empty string when no error exists, otherwise a prefixed note.
        """
        if error is None:
            return ""
        return f" Error: {error}"

    @staticmethod
    def _validate_unique_campaign_ids(scraped_rows: Sequence[ScrapedCampaignRow]) -> None:
        """Reject duplicate campaign IDs before aggregation.

        Args:
            scraped_rows: Panel rows to validate.

        Raises:
            DuplicateCampaignRowsError: If one or more campaign IDs appear more
                than once.
        """
        seen: set[str] = set()
        duplicates: set[str] = set()
        for row in scraped_rows:
            if row.campaign_id in seen:
                duplicates.add(row.campaign_id)
            seen.add(row.campaign_id)

        if duplicates:
            formatted_ids = ", ".join(sorted(duplicates))
            raise DuplicateCampaignRowsError(
                f"Scraped campaign rows contain duplicate campaign IDs: {formatted_ids}"
            )
