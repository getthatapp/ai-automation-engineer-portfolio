"""Playwright scraper for the local HTML-only marketing panel."""

from collections.abc import Sequence
from types import TracebackType
from typing import Protocol, Self, cast

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from marketing_ops_agent.browser.errors import (
    CampaignTableNotFoundError,
    DashboardUnavailableError,
    MalformedCampaignRowError,
    MarketingPanelLoginFailedError,
)
from marketing_ops_agent.config import AppConfig, load_config
from marketing_ops_agent.models import CampaignMetrics, Channel

LOGIN_USERNAME_SELECTOR = '[data-testid="username"]'
LOGIN_PASSWORD_SELECTOR = '[data-testid="password"]'
LOGIN_2FA_SELECTOR = '[data-testid="two-factor-code"]'
LOGIN_SUBMIT_SELECTOR = '[data-testid="sign-in"]'
CAMPAIGN_TABLE_SELECTOR = '[data-testid="campaign-table"]'
CAMPAIGN_ROW_SELECTOR = "tbody tr"
CAMPAIGN_CELL_SELECTOR = "td"
EXPECTED_CAMPAIGN_CELL_COUNT = 8


class LocatorLike(Protocol):
    """Minimal locator protocol used by the scraper and tests."""

    async def count(self) -> int:
        """Return the number of matched DOM nodes."""
        ...

    async def all(self) -> list["LocatorLike"]:
        """Return locator handles for all matched DOM nodes."""
        ...

    async def inner_text(self) -> str:
        """Return text content for a matched DOM node."""
        ...

    def locator(self, selector: str) -> "LocatorLike":
        """Return a nested locator for the provided selector."""
        ...


class PageLike(Protocol):
    """Minimal Playwright page protocol used by the scraper."""

    @property
    def url(self) -> str:
        """Return the current page URL."""
        ...

    async def goto(self, url: str, *, wait_until: str, timeout: float) -> object:
        """Navigate the browser page to a URL."""
        ...

    async def fill(self, selector: str, value: str) -> None:
        """Fill a form field matched by selector."""
        ...

    async def click(self, selector: str) -> None:
        """Click an element matched by selector."""
        ...

    async def wait_for_url(self, url: str, *, timeout: float) -> None:
        """Wait until the page URL matches the expected pattern."""
        ...

    def locator(self, selector: str) -> LocatorLike:
        """Return a locator for DOM nodes matching selector."""
        ...


class MarketingPanelCredentials(BaseModel):
    """Credentials for the local mock marketing panel."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    username: str = Field(min_length=1)
    password: str = Field(min_length=1)
    two_factor_code: str = Field(min_length=1)

    @classmethod
    def from_config(cls, config: AppConfig | None = None) -> "MarketingPanelCredentials":
        """Build mock panel credentials from application configuration.

        Args:
            config: Optional configuration object; environment defaults are used
                when omitted.

        Returns:
            Validated marketing panel credentials.
        """
        resolved_config = config or load_config()
        return cls(
            username=resolved_config.marketing_panel_username,
            password=resolved_config.marketing_panel_password,
            two_factor_code=resolved_config.marketing_panel_2fa_code,
        )


class ScrapedCampaignRow(BaseModel):
    """A campaign row scraped from the mock marketing dashboard table."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    campaign_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    channel: Channel
    impressions: int = Field(ge=0)
    clicks: int = Field(ge=0)
    conversions: int = Field(ge=0)
    cost: float = Field(ge=0)
    revenue: float = Field(ge=0)

    @field_validator("campaign_id", "name")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        """Trim required text fields and reject blank values.

        Args:
            value: Raw field value.

        Returns:
            Stripped non-empty value.

        Raises:
            ValueError: If the stripped value is blank.
        """
        stripped = value.strip()
        if not stripped:
            raise ValueError("value must not be blank")
        return stripped

    @classmethod
    def from_cells(cls, cells: Sequence[str]) -> "ScrapedCampaignRow":
        """Create a row model from table cell text."""

        if len(cells) != EXPECTED_CAMPAIGN_CELL_COUNT:
            raise MalformedCampaignRowError(
                f"Expected {EXPECTED_CAMPAIGN_CELL_COUNT} cells, got {len(cells)}"
            )

        try:
            return cls(
                campaign_id=cells[0],
                name=cells[1],
                channel=Channel(cells[2].strip()),
                impressions=_parse_int(cells[3]),
                clicks=_parse_int(cells[4]),
                conversions=_parse_int(cells[5]),
                cost=_parse_float(cells[6]),
                revenue=_parse_float(cells[7]),
            )
        except (ValueError, ValidationError) as exc:
            raise MalformedCampaignRowError("Campaign row contains invalid values") from exc

    def to_metrics(self) -> CampaignMetrics:
        """Convert scraped table values to the shared metrics model."""

        return CampaignMetrics(
            impressions=self.impressions,
            clicks=self.clicks,
            conversions=self.conversions,
            spend=self.cost,
            revenue=self.revenue,
        )


class PlaywrightMarketingPanelScraper:
    """Browser tool for scraping the local mock marketing panel."""

    def __init__(
        self,
        *,
        base_url: str | None = None,
        credentials: MarketingPanelCredentials | None = None,
        timeout_seconds: float | None = None,
        headless: bool = True,
        page: PageLike | None = None,
        config: AppConfig | None = None,
    ) -> None:
        """Initialize the scraper with browser, credential and timeout settings.

        Args:
            base_url: Optional mock panel base URL.
            credentials: Optional explicit panel credentials.
            timeout_seconds: Optional browser operation timeout.
            headless: Whether Playwright should launch Chromium headless.
            page: Optional injected page used by tests.
            config: Optional application configuration.
        """
        resolved_config = config or load_config()
        self._base_url = (base_url or resolved_config.marketing_panel_base_url).rstrip("/")
        self._credentials = credentials or MarketingPanelCredentials.from_config(resolved_config)
        self._timeout_ms = (timeout_seconds or resolved_config.request_timeout_seconds) * 1000
        self._headless = headless
        self._page = page

    async def __aenter__(self) -> Self:
        """Enter the async context manager without opening a browser yet."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Exit the async context manager.

        The scraper opens and closes Playwright browsers inside
        `scrape_campaign_rows`, so there is no persistent resource to close here.
        """
        return None

    async def scrape_campaign_rows(self) -> list[ScrapedCampaignRow]:
        """Log in to the local mock panel and scrape campaign table rows."""

        if self._page is not None:
            await self.login(self._page)
            return await self.scrape_dashboard(self._page)

        from playwright.async_api import async_playwright

        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=self._headless)
            try:
                page = await browser.new_page()
                panel_page = cast(PageLike, page)
                await self.login(panel_page)
                return await self.scrape_dashboard(panel_page)
            finally:
                await browser.close()

    async def login(self, page: PageLike) -> None:
        """Submit the mock panel login form."""

        await page.goto(
            self._url("/login"),
            wait_until="domcontentloaded",
            timeout=self._timeout_ms,
        )
        await page.fill(LOGIN_USERNAME_SELECTOR, self._credentials.username)
        await page.fill(LOGIN_PASSWORD_SELECTOR, self._credentials.password)
        await page.fill(LOGIN_2FA_SELECTOR, self._credentials.two_factor_code)
        await page.click(LOGIN_SUBMIT_SELECTOR)

        try:
            await page.wait_for_url("**/dashboard", timeout=self._timeout_ms)
        except Exception as exc:
            raise MarketingPanelLoginFailedError("Mock marketing panel login failed") from exc

        if not page.url.rstrip("/").endswith("/dashboard"):
            raise MarketingPanelLoginFailedError("Mock marketing panel did not reach dashboard")

    async def scrape_dashboard(self, page: PageLike) -> list[ScrapedCampaignRow]:
        """Scrape campaign rows from the current dashboard page."""

        if not page.url.rstrip("/").endswith("/dashboard"):
            await page.goto(
                self._url("/dashboard"),
                wait_until="domcontentloaded",
                timeout=self._timeout_ms,
            )

        if not page.url.rstrip("/").endswith("/dashboard"):
            raise DashboardUnavailableError("Mock marketing dashboard is unavailable")

        table = page.locator(CAMPAIGN_TABLE_SELECTOR)
        if await table.count() != 1:
            raise CampaignTableNotFoundError("Campaign table was not found on dashboard")

        row_locators = await table.locator(CAMPAIGN_ROW_SELECTOR).all()
        rows: list[ScrapedCampaignRow] = []
        for index, row_locator in enumerate(row_locators, start=1):
            rows.append(await self._scrape_row(row_locator, index))
        return rows

    async def _scrape_row(self, row_locator: LocatorLike, row_index: int) -> ScrapedCampaignRow:
        """Scrape and validate one campaign table row.

        Args:
            row_locator: Locator for a dashboard table row.
            row_index: One-based row index used in error messages.

        Returns:
            Validated scraped campaign row.

        Raises:
            MalformedCampaignRowError: If the row has invalid cell content.
        """
        cell_locators = await row_locator.locator(CAMPAIGN_CELL_SELECTOR).all()
        cells = [(await cell.inner_text()).strip() for cell in cell_locators]

        try:
            return ScrapedCampaignRow.from_cells(cells)
        except MalformedCampaignRowError as exc:
            raise MalformedCampaignRowError(f"Malformed campaign row {row_index}: {exc}") from exc

    def _url(self, path: str) -> str:
        """Build an absolute mock panel URL from a relative path.

        Args:
            path: Relative path with or without a leading slash.

        Returns:
            Absolute URL under the configured panel base URL.
        """
        return f"{self._base_url}{path if path.startswith('/') else f'/{path}'}"


def _parse_int(value: str) -> int:
    """Parse an integer from dashboard text that may contain separators."""
    return int(value.strip().replace(",", ""))


def _parse_float(value: str) -> float:
    """Parse a float from dashboard text that may contain separators."""
    return float(value.strip().replace(",", ""))
