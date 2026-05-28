"""Custom errors for marketing panel browser automation."""


class MarketingPanelScraperError(Exception):
    """Base error for marketing panel scraping failures."""


class MarketingPanelLoginFailedError(MarketingPanelScraperError):
    """Raised when the mock marketing panel login fails."""


class DashboardUnavailableError(MarketingPanelScraperError):
    """Raised when the marketing dashboard cannot be reached after login."""


class CampaignTableNotFoundError(MarketingPanelScraperError):
    """Raised when the dashboard campaign table is missing."""


class MalformedCampaignRowError(MarketingPanelScraperError):
    """Raised when a campaign table row does not match the expected shape."""
