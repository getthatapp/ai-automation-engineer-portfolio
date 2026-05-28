from html.parser import HTMLParser

import pytest

from marketing_ops_agent.browser.errors import (
    CampaignTableNotFoundError,
    MalformedCampaignRowError,
    MarketingPanelLoginFailedError,
)
from marketing_ops_agent.browser.panel_scraper import (
    LOGIN_2FA_SELECTOR,
    LOGIN_PASSWORD_SELECTOR,
    LOGIN_USERNAME_SELECTOR,
    MarketingPanelCredentials,
    PlaywrightMarketingPanelScraper,
)
from marketing_ops_agent.mock_services.marketing_panel import _render_dashboard


class CampaignTableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.rows: list[list[str]] = []
        self._in_campaign_table = False
        self._in_row = False
        self._in_cell = False
        self._current_row: list[str] = []
        self._current_cell: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "table" and attributes.get("data-testid") == "campaign-table":
            self._in_campaign_table = True
        elif self._in_campaign_table and tag == "tr":
            self._in_row = True
            self._current_row = []
        elif self._in_campaign_table and self._in_row and tag == "td":
            self._in_cell = True
            self._current_cell = []

    def handle_data(self, data: str) -> None:
        if self._in_cell:
            self._current_cell.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "td" and self._in_cell:
            self._current_row.append("".join(self._current_cell).strip())
            self._in_cell = False
        elif tag == "tr" and self._in_row:
            if self._current_row:
                self.rows.append(self._current_row)
            self._in_row = False
        elif tag == "table" and self._in_campaign_table:
            self._in_campaign_table = False


class FakeLocator:
    def __init__(
        self,
        *,
        text: str = "",
        children: list["FakeLocator"] | None = None,
        count_override: int | None = None,
    ) -> None:
        self._text = text
        self._children = children or []
        self._count_override = count_override

    async def count(self) -> int:
        if self._count_override is not None:
            return self._count_override
        if self._children:
            return len(self._children)
        return 1

    async def all(self) -> list["FakeLocator"]:
        return self._children

    async def inner_text(self) -> str:
        return self._text

    def locator(self, selector: str) -> "FakeLocator":
        if selector == "tbody tr":
            return FakeLocator(children=self._children)
        if selector == "td":
            return FakeLocator(children=self._children)
        return FakeLocator(count_override=0)


class FakePage:
    def __init__(
        self,
        *,
        rows: list[list[str]] | None,
        login_success: bool = True,
        base_url: str = "http://mock-panel.local",
    ) -> None:
        self._rows = rows
        self._login_success = login_success
        self._base_url = base_url
        self._url = ""
        self.fill_selectors: list[str] = []
        self.locator_selectors: list[str] = []

    @property
    def url(self) -> str:
        return self._url

    async def goto(self, url: str, *, wait_until: str, timeout: float) -> object:
        self._url = url
        return None

    async def fill(self, selector: str, value: str) -> None:
        self.fill_selectors.append(selector)

    async def click(self, selector: str) -> None:
        if self._login_success:
            self._url = f"{self._base_url}/dashboard"

    async def wait_for_url(self, url: str, *, timeout: float) -> None:
        if not self._login_success:
            raise RuntimeError("login did not redirect")

    def locator(self, selector: str) -> FakeLocator:
        self.locator_selectors.append(selector)
        if selector != '[data-testid="campaign-table"]' or self._rows is None:
            return FakeLocator(count_override=0)

        row_locators = [
            FakeLocator(children=[FakeLocator(text=cell) for cell in row])
            for row in self._rows
        ]
        return FakeLocator(children=row_locators, count_override=1)


@pytest.mark.asyncio
async def test_scraper_logs_in_and_scrapes_campaign_rows_from_mock_html() -> None:
    page = FakePage(rows=_dashboard_rows())
    scraper = PlaywrightMarketingPanelScraper(
        base_url="http://mock-panel.local",
        credentials=_credentials(),
        page=page,
    )

    rows = await scraper.scrape_campaign_rows()

    assert page.fill_selectors == [
        LOGIN_USERNAME_SELECTOR,
        LOGIN_PASSWORD_SELECTOR,
        LOGIN_2FA_SELECTOR,
    ]
    assert len(rows) == 3
    assert rows[0].campaign_id == "cmp-search-brand"
    assert rows[0].to_metrics().spend == 12_150.0


@pytest.mark.asyncio
async def test_scraper_raises_login_failed_for_bad_mock_credentials() -> None:
    page = FakePage(rows=_dashboard_rows(), login_success=False)
    scraper = PlaywrightMarketingPanelScraper(
        base_url="http://mock-panel.local",
        credentials=_credentials(),
        page=page,
    )

    with pytest.raises(MarketingPanelLoginFailedError):
        await scraper.scrape_campaign_rows()


@pytest.mark.asyncio
async def test_scraper_raises_when_campaign_table_is_missing() -> None:
    page = FakePage(rows=None)
    scraper = PlaywrightMarketingPanelScraper(
        base_url="http://mock-panel.local",
        credentials=_credentials(),
        page=page,
    )

    with pytest.raises(CampaignTableNotFoundError):
        await scraper.scrape_campaign_rows()


@pytest.mark.asyncio
async def test_scraper_raises_for_malformed_campaign_row() -> None:
    page = FakePage(rows=[["cmp-broken", "Broken Row"]])
    scraper = PlaywrightMarketingPanelScraper(
        base_url="http://mock-panel.local",
        credentials=_credentials(),
        page=page,
    )

    with pytest.raises(MalformedCampaignRowError):
        await scraper.scrape_campaign_rows()


@pytest.mark.asyncio
async def test_scraper_uses_only_mock_login_selectors() -> None:
    page = FakePage(rows=_dashboard_rows())
    scraper = PlaywrightMarketingPanelScraper(
        base_url="http://mock-panel.local",
        credentials=_credentials(),
        page=page,
    )

    await scraper.scrape_campaign_rows()

    queried_selectors = page.fill_selectors + page.locator_selectors
    assert queried_selectors
    assert all("captcha" not in selector.lower() for selector in queried_selectors)


def _dashboard_rows() -> list[list[str]]:
    parser = CampaignTableParser()
    parser.feed(_render_dashboard())
    return parser.rows


def _credentials() -> MarketingPanelCredentials:
    return MarketingPanelCredentials(
        username="demo@example.com",
        password="local-password",
        two_factor_code="000000",
    )
