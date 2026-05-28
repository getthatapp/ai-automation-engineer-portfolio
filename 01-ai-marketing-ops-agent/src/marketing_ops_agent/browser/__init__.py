"""Browser automation tools for HTML-only panels."""

from marketing_ops_agent.browser.errors import (
    CampaignTableNotFoundError,
    DashboardUnavailableError,
    MalformedCampaignRowError,
    MarketingPanelLoginFailedError,
    MarketingPanelScraperError,
)
from marketing_ops_agent.browser.panel_scraper import (
    MarketingPanelCredentials,
    PlaywrightMarketingPanelScraper,
    ScrapedCampaignRow,
)

__all__ = [
    "CampaignTableNotFoundError",
    "DashboardUnavailableError",
    "MalformedCampaignRowError",
    "MarketingPanelCredentials",
    "MarketingPanelLoginFailedError",
    "MarketingPanelScraperError",
    "PlaywrightMarketingPanelScraper",
    "ScrapedCampaignRow",
]
