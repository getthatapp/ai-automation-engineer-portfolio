from fastapi.testclient import TestClient

from marketing_ops_agent.mock_services.analytics_graphql_api import create_app


def test_graphql_returns_campaign_metrics_by_variable() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/graphql",
        json={
            "query": """
                query CampaignMetrics($campaignId: String!) {
                  campaignMetrics(campaignId: $campaignId) {
                    impressions
                    clicks
                    conversions
                    revenue
                    cost
                  }
                }
            """,
            "variables": {"campaignId": "cmp-search-brand"},
        },
    )

    assert response.status_code == 200
    payload = response.json()
    metrics = payload["data"]["campaignMetrics"]
    assert metrics["campaignId"] == "cmp-search-brand"
    assert "campaign_id" not in metrics
    assert metrics["impressions"] == 120_000
    assert metrics["cost"] == 12_150.0


def test_graphql_returns_all_campaign_metrics() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/graphql",
        json={
            "query": """
                query AllCampaignMetrics {
                  allCampaignMetrics {
                    campaignId
                    revenue
                    cost
                  }
                }
            """,
        },
    )

    assert response.status_code == 200
    metrics = response.json()["data"]["allCampaignMetrics"]
    assert len(metrics) == 3
    assert metrics[0]["campaignId"]
    assert "campaign_id" not in metrics[0]
