"""Typed client for the campaign REST API."""

from datetime import datetime

import httpx
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from marketing_ops_agent.clients._http import AsyncHttpServiceClient
from marketing_ops_agent.clients.errors import ServiceDecodeError
from marketing_ops_agent.config import AppConfig, load_config
from marketing_ops_agent.models import Campaign, Channel
from marketing_ops_agent.utils.retry import RetryConfig


class CampaignSummary(BaseModel):
    """Campaign summary returned by the list endpoint."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    campaign_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    channel: Channel
    collected_at: datetime


class CampaignClient:
    """Client for the campaign REST API."""

    def __init__(
        self,
        *,
        base_url: str | None = None,
        timeout_seconds: float | None = None,
        retry_config: RetryConfig | None = None,
        http_client: httpx.AsyncClient | None = None,
        config: AppConfig | None = None,
    ) -> None:
        """Initialize the Campaign REST API client.

        Args:
            base_url: Optional Campaign API base URL override.
            timeout_seconds: Per-call timeout override.
            retry_config: Retry policy for transient service failures.
            http_client: Optional injected HTTP client for tests.
            config: Optional application configuration.
        """
        resolved_config = config or load_config()
        self._http = AsyncHttpServiceClient(
            base_url=base_url or resolved_config.campaign_api_base_url,
            timeout_seconds=timeout_seconds,
            retry_config=retry_config,
            http_client=http_client,
            config=resolved_config,
        )

    async def __aenter__(self) -> "CampaignClient":
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

    async def list_campaigns(self) -> list[CampaignSummary]:
        """List campaigns from the REST API.

        Returns:
            Validated campaign summaries.

        Raises:
            ServiceDecodeError: If the response shape is invalid.
            ServiceClientError: If the HTTP request fails after retries.
        """

        payload = await self._http.request_json("GET", "/api/campaigns")
        if not isinstance(payload, list):
            raise ServiceDecodeError("Campaign list response must be a JSON array")

        try:
            return [CampaignSummary.model_validate(item) for item in payload]
        except ValidationError as exc:
            raise ServiceDecodeError("Campaign list response contains invalid items") from exc

    async def get_campaign(self, campaign_id: str) -> Campaign:
        """Get one campaign by ID.

        Args:
            campaign_id: Campaign identifier to fetch.

        Returns:
            Validated campaign detail.

        Raises:
            ServiceDecodeError: If the response shape is invalid.
            ServiceClientError: If the HTTP request fails after retries.
        """

        payload = await self._http.request_json("GET", f"/api/campaigns/{campaign_id}")
        try:
            return Campaign.model_validate(payload)
        except ValidationError as exc:
            raise ServiceDecodeError("Campaign detail response is invalid") from exc
