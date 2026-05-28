import httpx
import pytest

from marketing_ops_agent.clients.campaign_client import CampaignClient
from marketing_ops_agent.clients.errors import ServiceResponseError, ServiceTimeoutError
from marketing_ops_agent.utils.retry import RetryConfig


@pytest.mark.asyncio
async def test_campaign_client_lists_campaigns() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/api/campaigns"
        return httpx.Response(
            200,
            json=[
                {
                    "campaign_id": "cmp-search-brand",
                    "name": "Brand Search Defense",
                    "channel": "search",
                    "collected_at": "2026-05-28T08:00:00Z",
                }
            ],
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        client = CampaignClient(
            base_url="https://campaigns.example",
            http_client=http_client,
            retry_config=RetryConfig(max_attempts=1),
        )

        campaigns = await client.list_campaigns()

    assert campaigns[0].campaign_id == "cmp-search-brand"


@pytest.mark.asyncio
async def test_campaign_client_gets_campaign_by_id() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/campaigns/cmp-search-brand"
        return httpx.Response(
            200,
            json={
                "campaign_id": "cmp-search-brand",
                "name": "Brand Search Defense",
                "channel": "search",
                "source_url": None,
                "metrics": {
                    "impressions": 120_000,
                    "clicks": 8_200,
                    "conversions": 640,
                    "spend": 12_150.0,
                    "revenue": 38_400.0,
                },
                "collected_at": "2026-05-28T08:00:00Z",
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        client = CampaignClient(
            base_url="https://campaigns.example",
            http_client=http_client,
            retry_config=RetryConfig(max_attempts=1),
        )

        campaign = await client.get_campaign("cmp-search-brand")

    assert campaign.metrics.return_on_ad_spend == pytest.approx(38_400.0 / 12_150.0)


@pytest.mark.asyncio
async def test_campaign_client_retries_timeout_then_raises() -> None:
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        raise httpx.ConnectTimeout("timed out", request=request)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        client = CampaignClient(
            base_url="https://campaigns.example",
            http_client=http_client,
            retry_config=RetryConfig(max_attempts=2, initial_delay_seconds=0),
        )

        with pytest.raises(ServiceTimeoutError):
            await client.list_campaigns()

    assert attempts == 2


@pytest.mark.asyncio
async def test_campaign_client_raises_response_error_for_404() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"detail": "Campaign not found"})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        client = CampaignClient(
            base_url="https://campaigns.example",
            http_client=http_client,
            retry_config=RetryConfig(max_attempts=1),
        )

        with pytest.raises(ServiceResponseError) as error:
            await client.get_campaign("missing")

    assert error.value.status_code == 404
