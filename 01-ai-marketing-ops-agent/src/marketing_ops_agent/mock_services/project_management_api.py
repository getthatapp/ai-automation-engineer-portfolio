"""Mock project management REST API service."""

from datetime import UTC, datetime

from fastapi import FastAPI

from marketing_ops_agent.mock_services.schemas import TaskCreateRequest, TaskResponse


def create_app() -> FastAPI:
    """Create the project management REST API app."""

    app = FastAPI(title="Mock Project Management API", version="0.1.0")
    tasks: list[TaskResponse] = []

    @app.post("/api/tasks", response_model=TaskResponse, status_code=201)
    async def create_task(request: TaskCreateRequest) -> TaskResponse:
        task = TaskResponse(
            task_id=f"task-{len(tasks) + 1:03d}",
            title=request.title.strip(),
            description=request.description.strip(),
            campaign_id=request.campaign_id,
            status="open",
            created_at=datetime.now(UTC),
        )
        tasks.append(task)
        return task

    @app.get("/api/tasks", response_model=list[TaskResponse])
    async def get_tasks() -> list[TaskResponse]:
        return tasks

    return app


app = create_app()
