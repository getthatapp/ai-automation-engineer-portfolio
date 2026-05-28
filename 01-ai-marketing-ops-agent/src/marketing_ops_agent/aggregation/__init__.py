"""Campaign data aggregation package."""

from marketing_ops_agent.aggregation.aggregator import CampaignAggregator
from marketing_ops_agent.aggregation.campaign_snapshot import CampaignSnapshot
from marketing_ops_agent.aggregation.data_quality import DataQualityFlag
from marketing_ops_agent.aggregation.errors import (
    CampaignAggregationError,
    DuplicateCampaignRowsError,
)

__all__ = [
    "CampaignAggregationError",
    "CampaignAggregator",
    "CampaignSnapshot",
    "DataQualityFlag",
    "DuplicateCampaignRowsError",
]
