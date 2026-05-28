import httpx
import pytest

from marketing_ops_agent.clients.analytics_client import AnalyticsClient
from marketing_ops_agent.clients.errors import GraphQLResponseError, ServiceTimeoutError
from marketing_ops_agent.mock_services.analytics_graphql_api import create_app
from marketing_ops_agent.utils.retry import RetryConfig


@pytest.mark.asyncio
async def test_analytics_client_gets_campaign_metrics() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/graphql"
        return httpx.Response(
            200,
            json={
                "data": {
                    "campaignMetrics": {
                        "campaignId": "cmp-search-brand",
                        "impressions": 120_000,
                        "clicks": 8_200,
                        "conversions": 640,
                        "revenue": 38_400.0,
                        "cost": 12_150.0,
                    }
                }
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        client = AnalyticsClient(
            graphql_url="https://analytics.example/graphql",
            http_client=http_client,
            retry_config=RetryConfig(max_attempts=1),
        )

        metrics = await client.get_campaign_metrics("cmp-search-brand")

    assert metrics.campaign_id == "cmp-search-brand"
    assert metrics.cost == 12_150.0


@pytest.mark.asyncio
async def test_analytics_client_accepts_mock_graphql_api_response_shape() -> None:
    transport = httpx.ASGITransport(app=create_app())
    async with httpx.AsyncClient(transport=transport) as http_client:
        client = AnalyticsClient(
            graphql_url="http://testserver/graphql",
            http_client=http_client,
            retry_config=RetryConfig(max_attempts=1),
        )

        metrics = await client.get_campaign_metrics("cmp-search-brand")

    assert metrics.campaign_id == "cmp-search-brand"
    assert metrics.impressions == 120_000
    assert metrics.cost == 12_150.0


@pytest.mark.asyncio
async def test_analytics_client_raises_for_graphql_errors() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"errors": [{"message": "campaign not authorized"}], "data": None},
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        client = AnalyticsClient(
            graphql_url="https://analytics.example/graphql",
            http_client=http_client,
            retry_config=RetryConfig(max_attempts=1),
        )

        with pytest.raises(GraphQLResponseError) as error:
            await client.get_campaign_metrics("cmp-search-brand")

    assert "campaign not authorized" in str(error.value)


@pytest.mark.asyncio
async def test_analytics_client_raises_timeout_error() -> None:
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        raise httpx.ReadTimeout("timed out", request=request)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        client = AnalyticsClient(
            graphql_url="https://analytics.example/graphql",
            http_client=http_client,
            retry_config=RetryConfig(max_attempts=2, initial_delay_seconds=0),
        )

        with pytest.raises(ServiceTimeoutError):
            await client.get_campaign_metrics("cmp-search-brand")

    assert attempts == 2
