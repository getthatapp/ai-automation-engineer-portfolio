import httpx
import pytest

from marketing_ops_agent.clients.project_management_client import (
    ProjectManagementClient,
    ProjectTaskCreate,
)
from marketing_ops_agent.utils.retry import RetryConfig


@pytest.mark.asyncio
async def test_project_management_client_creates_task() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/api/tasks"
        return httpx.Response(
            201,
            json={
                "task_id": "task-001",
                "title": "Review high-spend search campaign",
                "description": "Check ROAS movement before changing budget.",
                "campaign_id": "cmp-search-brand",
                "status": "open",
                "created_at": "2026-05-28T08:00:00Z",
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        client = ProjectManagementClient(
            base_url="https://tasks.example",
            http_client=http_client,
            retry_config=RetryConfig(max_attempts=1),
        )

        task = await client.create_task(
            ProjectTaskCreate(
                title="Review high-spend search campaign",
                description="Check ROAS movement before changing budget.",
                campaign_id="cmp-search-brand",
            )
        )

    assert task.task_id == "task-001"
    assert task.status == "open"


@pytest.mark.asyncio
async def test_project_management_client_lists_tasks() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/api/tasks"
        return httpx.Response(
            200,
            json=[
                {
                    "task_id": "task-001",
                    "title": "Review high-spend search campaign",
                    "description": "Check ROAS movement before changing budget.",
                    "campaign_id": "cmp-search-brand",
                    "status": "open",
                    "created_at": "2026-05-28T08:00:00Z",
                }
            ],
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        client = ProjectManagementClient(
            base_url="https://tasks.example",
            http_client=http_client,
            retry_config=RetryConfig(max_attempts=1),
        )

        tasks = await client.list_tasks()

    assert len(tasks) == 1
    assert tasks[0].campaign_id == "cmp-search-brand"
