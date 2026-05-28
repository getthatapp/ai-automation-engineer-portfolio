"""Pydantic schemas used by the local mock services."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from marketing_ops_agent.models import Campaign, Channel


class CampaignSummary(BaseModel):
    """REST summary for a campaign."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    campaign_id: str
    name: str
    channel: Channel
    collected_at: datetime

    @classmethod
    def from_campaign(cls, campaign: Campaign) -> "CampaignSummary":
        """Build a REST campaign summary from the shared campaign model.

        Args:
            campaign: Internal campaign fixture model.

        Returns:
            Mock REST summary schema.
        """
        return cls(
            campaign_id=campaign.campaign_id,
            name=campaign.name,
            channel=campaign.channel,
            collected_at=campaign.collected_at,
        )


class AnalyticsMetrics(BaseModel):
    """GraphQL-facing analytics metrics."""

    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    campaign_id: str = Field(alias="campaignId")
    impressions: int = Field(ge=0)
    clicks: int = Field(ge=0)
    conversions: int = Field(ge=0)
    revenue: float = Field(ge=0)
    cost: float = Field(ge=0)

    @classmethod
    def from_campaign(cls, campaign: Campaign) -> "AnalyticsMetrics":
        """Build GraphQL analytics metrics from the shared campaign model.

        Args:
            campaign: Internal campaign fixture model.

        Returns:
            Mock GraphQL metrics schema.
        """
        return cls(
            campaignId=campaign.campaign_id,
            impressions=campaign.metrics.impressions,
            clicks=campaign.metrics.clicks,
            conversions=campaign.metrics.conversions,
            revenue=campaign.metrics.revenue,
            cost=campaign.metrics.spend,
        )


class GraphQLRequest(BaseModel):
    """Minimal GraphQL request body accepted by the analytics mock."""

    model_config = ConfigDict(extra="forbid")

    query: str = Field(min_length=1)
    variables: dict[str, str] | None = None


class TaskCreateRequest(BaseModel):
    """Request body for creating a project management task."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1)
    description: str = Field(default="", max_length=2_000)
    campaign_id: str | None = None


class TaskResponse(BaseModel):
    """Project management task response."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    task_id: str
    title: str
    description: str
    campaign_id: str | None
    status: str
    created_at: datetime
