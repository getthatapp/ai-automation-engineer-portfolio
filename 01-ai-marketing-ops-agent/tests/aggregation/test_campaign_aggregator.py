from collections.abc import Mapping
from datetime import UTC, datetime, timedelta

import pytest

from marketing_ops_agent.aggregation import (
    CampaignAggregator,
    DataQualityFlag,
    DuplicateCampaignRowsError,
)
from marketing_ops_agent.browser.panel_scraper import ScrapedCampaignRow
from marketing_ops_agent.clients.analytics_client import AnalyticsCampaignMetrics
from marketing_ops_agent.clients.errors import ServiceDecodeError, ServiceResponseError
from marketing_ops_agent.models import Campaign, CampaignMetrics, Channel

REFERENCE_TIME = datetime(2026, 5, 28, 12, 0, tzinfo=UTC)


class FakeCampaignClient:
    def __init__(self, campaigns: Mapping[str, Campaign]) -> None:
        self._campaigns = campaigns

    async def get_campaign(self, campaign_id: str) -> Campaign:
        campaign = self._campaigns.get(campaign_id)
        if campaign is None:
            raise ServiceResponseError(status_code=404, response_text="Campaign not found")
        return campaign


class FakeAnalyticsClient:
    def __init__(self, metrics: Mapping[str, AnalyticsCampaignMetrics]) -> None:
        self._metrics = metrics

    async def get_campaign_metrics(self, campaign_id: str) -> AnalyticsCampaignMetrics:
        metrics = self._metrics.get(campaign_id)
        if metrics is None:
            raise ServiceDecodeError("GraphQL response is missing campaignMetrics")
        return metrics


@pytest.mark.asyncio
async def test_aggregates_happy_path_campaign_snapshot() -> None:
    row = _row()
    campaign = _campaign()
    analytics_metrics = _analytics_metrics()
    aggregator = _aggregator(
        campaigns={row.campaign_id: campaign},
        metrics={row.campaign_id: analytics_metrics},
    )

    snapshots = await aggregator.aggregate([row], reference_time=REFERENCE_TIME)

    assert len(snapshots) == 1
    snapshot = snapshots[0]
    assert snapshot.campaign_id == row.campaign_id
    assert snapshot.scraped_row == row
    assert snapshot.campaign_metadata == campaign
    assert snapshot.analytics_metrics == analytics_metrics
    assert snapshot.data_quality_flags == ()
    assert snapshot.requires_human_review is False


@pytest.mark.asyncio
async def test_marks_missing_campaign_api_data_without_dropping_row() -> None:
    row = _row()
    aggregator = _aggregator(campaigns={}, metrics={row.campaign_id: _analytics_metrics()})

    snapshots = await aggregator.aggregate([row], reference_time=REFERENCE_TIME)

    snapshot = snapshots[0]
    assert snapshot.scraped_row == row
    assert snapshot.campaign_metadata is None
    assert DataQualityFlag.MISSING_CAMPAIGN_METADATA in snapshot.data_quality_flags
    assert snapshot.requires_human_review is True


@pytest.mark.asyncio
async def test_marks_missing_graphql_metrics_without_dropping_metadata() -> None:
    row = _row()
    campaign = _campaign()
    aggregator = _aggregator(campaigns={row.campaign_id: campaign}, metrics={})

    snapshots = await aggregator.aggregate([row], reference_time=REFERENCE_TIME)

    snapshot = snapshots[0]
    assert snapshot.campaign_metadata == campaign
    assert snapshot.analytics_metrics is None
    assert DataQualityFlag.MISSING_ANALYTICS_METRICS in snapshot.data_quality_flags
    assert snapshot.requires_human_review is True


@pytest.mark.asyncio
async def test_marks_spend_mismatch() -> None:
    row = _row(cost=12_999.0)
    aggregator = _aggregator(
        campaigns={row.campaign_id: _campaign()},
        metrics={row.campaign_id: _analytics_metrics()},
    )

    snapshots = await aggregator.aggregate([row], reference_time=REFERENCE_TIME)

    assert DataQualityFlag.SPEND_MISMATCH in snapshots[0].data_quality_flags


@pytest.mark.asyncio
async def test_marks_conversion_mismatch() -> None:
    row = _row()
    analytics_metrics = _analytics_metrics(conversions=641)
    aggregator = _aggregator(
        campaigns={row.campaign_id: _campaign()},
        metrics={row.campaign_id: analytics_metrics},
    )

    snapshots = await aggregator.aggregate([row], reference_time=REFERENCE_TIME)

    assert DataQualityFlag.CONVERSIONS_MISMATCH in snapshots[0].data_quality_flags


@pytest.mark.asyncio
async def test_marks_multiple_data_quality_flags() -> None:
    row = _row(cost=13_000.0)
    stale_campaign = _campaign(collected_at=REFERENCE_TIME - timedelta(days=3))
    analytics_metrics = _analytics_metrics(revenue=39_000.0)
    aggregator = _aggregator(
        campaigns={row.campaign_id: stale_campaign},
        metrics={row.campaign_id: analytics_metrics},
    )

    snapshots = await aggregator.aggregate([row], reference_time=REFERENCE_TIME)

    flags = snapshots[0].data_quality_flags
    assert DataQualityFlag.STALE_DATA in flags
    assert DataQualityFlag.SPEND_MISMATCH in flags
    assert DataQualityFlag.REVENUE_MISMATCH in flags


@pytest.mark.asyncio
async def test_requires_human_review_when_critical_mismatch_exists() -> None:
    row = _row()
    campaign = _campaign(conversions=999)
    aggregator = _aggregator(
        campaigns={row.campaign_id: campaign},
        metrics={row.campaign_id: _analytics_metrics()},
    )

    snapshots = await aggregator.aggregate([row], reference_time=REFERENCE_TIME)

    assert DataQualityFlag.CONVERSIONS_MISMATCH in snapshots[0].data_quality_flags
    assert DataQualityFlag.REQUIRES_HUMAN_REVIEW in snapshots[0].data_quality_flags
    assert snapshots[0].requires_human_review is True


@pytest.mark.asyncio
async def test_raises_when_scraped_rows_have_duplicate_campaign_ids() -> None:
    row = _row()
    aggregator = _aggregator(
        campaigns={row.campaign_id: _campaign()},
        metrics={row.campaign_id: _analytics_metrics()},
    )

    with pytest.raises(DuplicateCampaignRowsError):
        await aggregator.aggregate([row, row], reference_time=REFERENCE_TIME)


def _aggregator(
    *,
    campaigns: Mapping[str, Campaign],
    metrics: Mapping[str, AnalyticsCampaignMetrics],
) -> CampaignAggregator:
    return CampaignAggregator(
        campaign_client=FakeCampaignClient(campaigns),
        analytics_client=FakeAnalyticsClient(metrics),
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


def _campaign(
    *,
    conversions: int = 640,
    spend: float = 12_150.0,
    revenue: float = 38_400.0,
    collected_at: datetime = datetime(2026, 5, 28, 8, 0, tzinfo=UTC),
) -> Campaign:
    return Campaign(
        campaign_id="cmp-search-brand",
        name="Brand Search Defense",
        channel=Channel.SEARCH,
        metrics=CampaignMetrics(
            impressions=120_000,
            clicks=8_200,
            conversions=conversions,
            spend=spend,
            revenue=revenue,
        ),
        collected_at=collected_at,
    )


def _analytics_metrics(
    *,
    conversions: int = 640,
    cost: float = 12_150.0,
    revenue: float = 38_400.0,
) -> AnalyticsCampaignMetrics:
    return AnalyticsCampaignMetrics(
        campaignId="cmp-search-brand",
        impressions=120_000,
        clicks=8_200,
        conversions=conversions,
        revenue=revenue,
        cost=cost,
    )
