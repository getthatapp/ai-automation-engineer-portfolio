from fastapi.testclient import TestClient

from marketing_ops_agent.mock_services.project_management_api import create_app


def test_project_management_api_creates_and_lists_tasks() -> None:
    client = TestClient(create_app())

    create_response = client.post(
        "/api/tasks",
        json={
            "title": "Review high-spend search campaign",
            "description": "Check ROAS movement before changing budget.",
            "campaign_id": "cmp-search-brand",
        },
    )
    list_response = client.get("/api/tasks")

    assert create_response.status_code == 201
    task = create_response.json()
    assert task["task_id"] == "task-001"
    assert task["status"] == "open"
    assert list_response.json() == [task]


def test_project_management_api_starts_with_empty_task_list() -> None:
    client = TestClient(create_app())

    response = client.get("/api/tasks")

    assert response.status_code == 200
    assert response.json() == []
