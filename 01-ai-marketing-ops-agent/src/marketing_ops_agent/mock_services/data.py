"""Deterministic fake data shared by local mock services."""

from datetime import UTC, datetime

from marketing_ops_agent.models import Campaign, CampaignMetrics, Channel

COLLECTED_AT = datetime(2026, 5, 28, 8, 0, tzinfo=UTC)

CAMPAIGNS: tuple[Campaign, ...] = (
    Campaign(
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
        collected_at=COLLECTED_AT,
    ),
    Campaign(
        campaign_id="cmp-social-retargeting",
        name="Retargeting Social",
        channel=Channel.SOCIAL,
        metrics=CampaignMetrics(
            impressions=95_000,
            clicks=4_850,
            conversions=310,
            spend=9_800.0,
            revenue=21_700.0,
        ),
        collected_at=COLLECTED_AT,
    ),
    Campaign(
        campaign_id="cmp-email-winback",
        name="Email Winback",
        channel=Channel.EMAIL,
        metrics=CampaignMetrics(
            impressions=42_000,
            clicks=3_600,
            conversions=410,
            spend=1_200.0,
            revenue=18_900.0,
        ),
        collected_at=COLLECTED_AT,
    ),
)


def list_campaigns() -> tuple[Campaign, ...]:
    """Return the deterministic campaign fixture set."""

    return CAMPAIGNS


def get_campaign(campaign_id: str) -> Campaign | None:
    """Return one campaign fixture by ID."""

    return next((campaign for campaign in CAMPAIGNS if campaign.campaign_id == campaign_id), None)
