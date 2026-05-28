from fastapi.testclient import TestClient

from marketing_ops_agent.mock_services.campaign_api import create_app


def test_campaign_api_lists_campaigns() -> None:
    client = TestClient(create_app())

    response = client.get("/api/campaigns")

    assert response.status_code == 200
    campaigns = response.json()
    assert len(campaigns) == 3
    assert campaigns[0]["campaign_id"] == "cmp-search-brand"


def test_campaign_api_returns_campaign_detail() -> None:
    client = TestClient(create_app())

    response = client.get("/api/campaigns/cmp-email-winback")

    assert response.status_code == 200
    campaign = response.json()
    assert campaign["metrics"]["conversions"] == 410


def test_campaign_api_returns_404_for_unknown_campaign() -> None:
    client = TestClient(create_app())

    response = client.get("/api/campaigns/missing")

    assert response.status_code == 404
