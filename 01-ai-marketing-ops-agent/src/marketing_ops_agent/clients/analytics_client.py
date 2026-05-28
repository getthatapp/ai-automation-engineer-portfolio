"""Typed client for the analytics GraphQL API."""

from collections.abc import Mapping
from urllib.parse import urlsplit

import httpx
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from marketing_ops_agent.clients._http import AsyncHttpServiceClient
from marketing_ops_agent.clients.errors import GraphQLResponseError, ServiceDecodeError
from marketing_ops_agent.config import AppConfig, load_config
from marketing_ops_agent.utils.retry import RetryConfig


class AnalyticsCampaignMetrics(BaseModel):
    """Campaign metrics returned by the analytics GraphQL API."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    campaign_id: str = Field(alias="campaignId")
    impressions: int = Field(ge=0)
    clicks: int = Field(ge=0)
    conversions: int = Field(ge=0)
    revenue: float = Field(ge=0)
    cost: float = Field(ge=0)


class AnalyticsClient:
    """Client for querying analytics metrics through GraphQL."""

    def __init__(
        self,
        *,
        graphql_url: str | None = None,
        timeout_seconds: float | None = None,
        retry_config: RetryConfig | None = None,
        http_client: httpx.AsyncClient | None = None,
        config: AppConfig | None = None,
    ) -> None:
        """Initialize the Analytics GraphQL client.

        Args:
            graphql_url: Optional GraphQL endpoint URL override.
            timeout_seconds: Per-call timeout override.
            retry_config: Retry policy for transient service failures.
            http_client: Optional injected HTTP client for tests.
            config: Optional application configuration.
        """
        resolved_config = config or load_config()
        self._graphql_path = _extract_graphql_path(
            graphql_url or resolved_config.analytics_graphql_url
        )
        self._http = AsyncHttpServiceClient(
            base_url=_extract_base_url(graphql_url or resolved_config.analytics_graphql_url),
            timeout_seconds=timeout_seconds,
            retry_config=retry_config,
            http_client=http_client,
            config=resolved_config,
        )

    async def __aenter__(self) -> "AnalyticsClient":
        """Enter the async client context."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: object,
    ) -> None:
        """Exit the async client context and close owned HTTP resources."""
        await self.aclose()

    async def aclose(self) -> None:
        """Close the underlying HTTP client when owned by this instance."""

        await self._http.aclose()

    async def get_campaign_metrics(self, campaign_id: str) -> AnalyticsCampaignMetrics:
        """Return analytics metrics for one campaign ID.

        Args:
            campaign_id: Campaign identifier to query.

        Returns:
            Validated analytics metrics.

        Raises:
            GraphQLResponseError: If the GraphQL response contains errors.
            ServiceDecodeError: If the response shape is invalid.
            ServiceClientError: If the HTTP request fails after retries.
        """

        payload = await self._http.request_json(
            "POST",
            self._graphql_path,
            json_body={
                "query": """
                    query CampaignMetrics($campaignId: String!) {
                      campaignMetrics(campaignId: $campaignId) {
                        campaignId
                        impressions
                        clicks
                        conversions
                        revenue
                        cost
                      }
                    }
                """,
                "variables": {"campaignId": campaign_id},
            },
        )
        response_body = _require_mapping(payload)

        errors = response_body.get("errors")
        if errors is not None:
            raise GraphQLResponseError(errors)

        data = response_body.get("data")
        if not isinstance(data, Mapping):
            raise ServiceDecodeError("GraphQL response is missing data")

        metrics = data.get("campaignMetrics")
        if not isinstance(metrics, Mapping):
            raise ServiceDecodeError("GraphQL response is missing campaignMetrics")

        try:
            return AnalyticsCampaignMetrics.model_validate(metrics)
        except ValidationError as exc:
            raise ServiceDecodeError("GraphQL campaignMetrics payload is invalid") from exc


def _require_mapping(payload: object) -> Mapping[str, object]:
    """Require a decoded JSON payload to be an object mapping.

    Args:
        payload: Decoded JSON payload.

    Returns:
        Mapping payload.

    Raises:
        ServiceDecodeError: If the payload is not a mapping.
    """
    if not isinstance(payload, Mapping):
        raise ServiceDecodeError("GraphQL response must be a JSON object")
    return payload


def _extract_base_url(graphql_url: str) -> str:
    """Extract the HTTP base URL from a GraphQL endpoint URL.

    Args:
        graphql_url: Absolute GraphQL endpoint URL.

    Returns:
        Scheme and host portion of the endpoint.

    Raises:
        ValueError: If the URL is not absolute.
    """
    parsed = urlsplit(graphql_url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError("graphql_url must be an absolute URL")
    return f"{parsed.scheme}://{parsed.netloc}"


def _extract_graphql_path(graphql_url: str) -> str:
    """Extract the GraphQL request path from an endpoint URL.

    Args:
        graphql_url: Absolute GraphQL endpoint URL.

    Returns:
        URL path, defaulting to `/graphql` when empty.
    """
    parsed = urlsplit(graphql_url)
    return parsed.path or "/graphql"
