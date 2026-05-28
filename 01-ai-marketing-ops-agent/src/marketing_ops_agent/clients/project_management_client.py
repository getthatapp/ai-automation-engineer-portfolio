"""Typed client for the project management REST API."""

from datetime import datetime

import httpx
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from marketing_ops_agent.clients._http import AsyncHttpServiceClient
from marketing_ops_agent.clients.errors import ServiceDecodeError
from marketing_ops_agent.config import AppConfig, load_config
from marketing_ops_agent.utils.retry import RetryConfig


class ProjectTaskCreate(BaseModel):
    """Request body for creating a project management task."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    title: str = Field(min_length=1)
    description: str = Field(default="", max_length=2_000)
    campaign_id: str | None = None


class ProjectTask(BaseModel):
    """Project management task returned by the mock API."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    task_id: str
    title: str
    description: str
    campaign_id: str | None
    status: str
    created_at: datetime


class ProjectManagementClient:
    """Client for the project management REST API."""

    def __init__(
        self,
        *,
        base_url: str | None = None,
        timeout_seconds: float | None = None,
        retry_config: RetryConfig | None = None,
        http_client: httpx.AsyncClient | None = None,
        config: AppConfig | None = None,
    ) -> None:
        """Initialize the Project Management REST API client.

        Args:
            base_url: Optional project management API base URL override.
            timeout_seconds: Per-call timeout override.
            retry_config: Retry policy for transient service failures.
            http_client: Optional injected HTTP client for tests.
            config: Optional application configuration.
        """
        resolved_config = config or load_config()
        self._http = AsyncHttpServiceClient(
            base_url=base_url or resolved_config.project_management_api_base_url,
            timeout_seconds=timeout_seconds,
            retry_config=retry_config,
            http_client=http_client,
            config=resolved_config,
        )

    async def __aenter__(self) -> "ProjectManagementClient":
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

    async def create_task(self, task: ProjectTaskCreate) -> ProjectTask:
        """Create a project management task through the mock REST API.

        Args:
            task: Validated task creation request.

        Returns:
            Created task returned by the service.

        Raises:
            ServiceDecodeError: If the response shape is invalid.
            ServiceClientError: If the HTTP request fails after retries.
        """

        payload = await self._http.request_json(
            "POST",
            "/api/tasks",
            json_body=task.model_dump(),
        )
        try:
            return ProjectTask.model_validate(payload)
        except ValidationError as exc:
            raise ServiceDecodeError("Task creation response is invalid") from exc

    async def list_tasks(self) -> list[ProjectTask]:
        """List project management tasks from the mock REST API.

        Returns:
            Validated project tasks.

        Raises:
            ServiceDecodeError: If the response shape is invalid.
            ServiceClientError: If the HTTP request fails after retries.
        """

        payload = await self._http.request_json("GET", "/api/tasks")
        if not isinstance(payload, list):
            raise ServiceDecodeError("Task list response must be a JSON array")

        try:
            return [ProjectTask.model_validate(item) for item in payload]
        except ValidationError as exc:
            raise ServiceDecodeError("Task list response contains invalid items") from exc
