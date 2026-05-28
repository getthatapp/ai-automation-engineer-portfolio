"""Mock marketing panel without an API.

This app intentionally exposes campaign data only as HTML. Later Playwright
automation should use this service for browser-panel automation practice.
"""

from html import escape
from urllib.parse import parse_qs

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response

from marketing_ops_agent.mock_services.data import list_campaigns

SESSION_COOKIE_NAME = "mock_marketing_panel_session"
SESSION_COOKIE_VALUE = "local-demo-session"
DEMO_USERNAME = "demo@example.com"
DEMO_PASSWORD = "local-password"
DEMO_2FA_CODE = "000000"


def create_app() -> FastAPI:
    """Create the mock marketing panel app."""

    app = FastAPI(title="Mock Marketing Panel", version="0.1.0")

    @app.get("/login", response_class=HTMLResponse)
    async def login_page() -> str:
        """Return the mock panel login HTML page."""
        return _render_login_page()

    @app.post("/login")
    async def login(request: Request) -> Response:
        """Validate mock credentials and set a local session cookie.

        Args:
            request: Incoming form post request.

        Returns:
            Redirect response on success or login page with an error on failure.

        Side Effects:
            Sets a mock session cookie for valid credentials.
        """
        form = _parse_form_body(await request.body())
        username = form.get("username", "")
        password = form.get("password", "")
        two_factor_code = form.get("two_factor_code", "")

        if (
            username == DEMO_USERNAME
            and password == DEMO_PASSWORD
            and two_factor_code == DEMO_2FA_CODE
        ):
            response = RedirectResponse(url="/dashboard", status_code=303)
            response.set_cookie(
                key=SESSION_COOKIE_NAME,
                value=SESSION_COOKIE_VALUE,
                httponly=True,
                samesite="lax",
            )
            return response

        return HTMLResponse(_render_login_page(error="Invalid mock credentials"), status_code=401)

    @app.get("/dashboard", response_class=HTMLResponse)
    async def dashboard(request: Request) -> Response:
        """Return the dashboard HTML when the mock session cookie is present.

        Args:
            request: Incoming browser request.

        Returns:
            Dashboard HTML response or redirect to login.
        """
        if request.cookies.get(SESSION_COOKIE_NAME) != SESSION_COOKIE_VALUE:
            return RedirectResponse(url="/login", status_code=303)
        return HTMLResponse(_render_dashboard())

    return app


def _parse_form_body(body: bytes) -> dict[str, str]:
    """Parse URL-encoded login form data into single-value fields.

    Args:
        body: Raw request body bytes.

    Returns:
        Mapping of form field names to first submitted value.
    """
    parsed = parse_qs(body.decode("utf-8"), keep_blank_values=True)
    return {key: values[0] for key, values in parsed.items()}


def _render_login_page(error: str | None = None) -> str:
    """Render the login page HTML for the mock panel.

    Args:
        error: Optional escaped error message to show above the form.

    Returns:
        Complete HTML document string.
    """
    error_html = f'<p class="error">{escape(error)}</p>' if error else ""
    return f"""
<!doctype html>
<html lang="en">
  <head>
    <title>Mock Marketing Panel Login</title>
  </head>
  <body>
    <main>
      <h1>Mock Marketing Panel</h1>
      {error_html}
      <form method="post" action="/login" data-testid="login-form">
        <label>
          Email
          <input
            name="username"
            data-testid="username"
            type="email"
            autocomplete="username"
            required
          >
        </label>
        <label>
          Password
          <input
            name="password"
            data-testid="password"
            type="password"
            autocomplete="current-password"
            required
          >
        </label>
        <label>
          Mock 2FA code
          <input
            name="two_factor_code"
            data-testid="two-factor-code"
            inputmode="numeric"
            autocomplete="one-time-code"
            required
          >
        </label>
        <button type="submit" data-testid="sign-in">Sign in</button>
      </form>
    </main>
  </body>
</html>
""".strip()


def _render_dashboard() -> str:
    """Render campaign table HTML for the mock dashboard.

    Returns:
        Complete HTML document string containing deterministic campaign rows.
    """
    rows = "\n".join(
        f"""
        <tr data-campaign-id="{escape(campaign.campaign_id)}">
          <td>{escape(campaign.campaign_id)}</td>
          <td>{escape(campaign.name)}</td>
          <td>{escape(campaign.channel.value)}</td>
          <td>{campaign.metrics.impressions}</td>
          <td>{campaign.metrics.clicks}</td>
          <td>{campaign.metrics.conversions}</td>
          <td>{campaign.metrics.spend:.2f}</td>
          <td>{campaign.metrics.revenue:.2f}</td>
        </tr>
        """.strip()
        for campaign in list_campaigns()
    )

    return f"""
<!doctype html>
<html lang="en">
  <head>
    <title>Mock Marketing Dashboard</title>
  </head>
  <body>
    <main>
      <h1>Campaign Dashboard</h1>
      <table id="campaign-table" data-testid="campaign-table">
        <thead>
          <tr>
            <th>Campaign ID</th>
            <th>Name</th>
            <th>Channel</th>
            <th>Impressions</th>
            <th>Clicks</th>
            <th>Conversions</th>
            <th>Cost</th>
            <th>Revenue</th>
          </tr>
        </thead>
        <tbody>
          {rows}
        </tbody>
      </table>
    </main>
  </body>
</html>
""".strip()


app = create_app()
