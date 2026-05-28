"""Unified campaign snapshot model produced by the aggregation layer."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from marketing_ops_agent.aggregation.data_quality import DataQualityFlag
from marketing_ops_agent.browser.panel_scraper import ScrapedCampaignRow
from marketing_ops_agent.clients.analytics_client import AnalyticsCampaignMetrics
from marketing_ops_agent.models import Campaign


class CampaignSnapshot(BaseModel):
    """Validated campaign snapshot with source data and quality markers."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    campaign_id: str = Field(min_length=1)
    scraped_row: ScrapedCampaignRow
    campaign_metadata: Campaign | None = None
    analytics_metrics: AnalyticsCampaignMetrics | None = None
    data_quality_flags: tuple[DataQualityFlag, ...] = ()
    data_quality_notes: tuple[str, ...] = ()
    requires_human_review: bool = False
    aggregated_at: datetime
