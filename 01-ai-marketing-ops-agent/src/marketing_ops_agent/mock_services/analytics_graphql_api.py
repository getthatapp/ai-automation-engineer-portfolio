"""Mock analytics GraphQL API service."""

import re

from fastapi import FastAPI, HTTPException

from marketing_ops_agent.mock_services.data import get_campaign, list_campaigns
from marketing_ops_agent.mock_services.schemas import AnalyticsMetrics, GraphQLRequest

INLINE_CAMPAIGN_ID_RE = re.compile(r'campaignId\s*:\s*"(?P<campaign_id>[^"]+)"')


def create_app() -> FastAPI:
    """Create the analytics GraphQL API app."""

    app = FastAPI(title="Mock Analytics GraphQL API", version="0.1.0")

    @app.post("/graphql")
    async def graphql(request: GraphQLRequest) -> dict[str, object]:
        if "campaignMetrics" in request.query:
            campaign_id = _extract_campaign_id(request)
            campaign = get_campaign(campaign_id)
            if campaign is None:
                return {"data": {"campaignMetrics": None}}
            campaign_metrics = AnalyticsMetrics.from_campaign(campaign)
            return {"data": {"campaignMetrics": campaign_metrics.model_dump(by_alias=True)}}

        if "allCampaignMetrics" in request.query:
            all_metrics = [
                AnalyticsMetrics.from_campaign(campaign).model_dump(by_alias=True)
                for campaign in list_campaigns()
            ]
            return {"data": {"allCampaignMetrics": all_metrics}}

        raise HTTPException(status_code=400, detail="Unsupported GraphQL query")

    return app


def _extract_campaign_id(request: GraphQLRequest) -> str:
    if request.variables and "campaignId" in request.variables:
        return request.variables["campaignId"]

    inline_match = INLINE_CAMPAIGN_ID_RE.search(request.query)
    if inline_match is not None:
        return inline_match.group("campaign_id")

    raise HTTPException(status_code=400, detail="campaignId variable is required")


app = create_app()
