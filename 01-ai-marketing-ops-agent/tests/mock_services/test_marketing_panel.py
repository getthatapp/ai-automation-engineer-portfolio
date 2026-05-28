from fastapi.testclient import TestClient

from marketing_ops_agent.mock_services.marketing_panel import (
    DEMO_2FA_CODE,
    DEMO_PASSWORD,
    DEMO_USERNAME,
    create_app,
)


def test_login_page_contains_mock_2fa_field() -> None:
    client = TestClient(create_app())

    response = client.get("/login")

    assert response.status_code == 200
    assert 'name="two_factor_code"' in response.text
    assert "Mock 2FA code" in response.text


def test_dashboard_requires_login() -> None:
    client = TestClient(create_app(), follow_redirects=False)

    response = client.get("/dashboard")

    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_login_allows_dashboard_access_with_mock_credentials() -> None:
    client = TestClient(create_app())

    login_response = client.post(
        "/login",
        data={
            "username": DEMO_USERNAME,
            "password": DEMO_PASSWORD,
            "two_factor_code": DEMO_2FA_CODE,
        },
    )
    dashboard_response = client.get("/dashboard")

    assert login_response.status_code == 200
    assert dashboard_response.status_code == 200
    assert 'id="campaign-table"' in dashboard_response.text
    assert 'data-testid="campaign-table"' in dashboard_response.text
    assert "cmp-search-brand" in dashboard_response.text
