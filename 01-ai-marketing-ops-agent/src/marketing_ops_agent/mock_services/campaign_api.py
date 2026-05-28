"""Mock campaign REST API service."""

from fastapi import FastAPI, HTTPException

from marketing_ops_agent.mock_services.data import get_campaign, list_campaigns
from marketing_ops_agent.mock_services.schemas import CampaignSummary
from marketing_ops_agent.models import Campaign


def create_app() -> FastAPI:
    """Create the campaign REST API app."""

    app = FastAPI(title="Mock Campaign REST API", version="0.1.0")

    @app.get("/api/campaigns", response_model=list[CampaignSummary])
    async def get_campaigns() -> list[CampaignSummary]:
        return [CampaignSummary.from_campaign(campaign) for campaign in list_campaigns()]

    @app.get("/api/campaigns/{campaign_id}", response_model=Campaign)
    async def get_campaign_by_id(campaign_id: str) -> Campaign:
        campaign = get_campaign(campaign_id)
        if campaign is None:
            raise HTTPException(status_code=404, detail="Campaign not found")
        return campaign

    return app


app = create_app()
