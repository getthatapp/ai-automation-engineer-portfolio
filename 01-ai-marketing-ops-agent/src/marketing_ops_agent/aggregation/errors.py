"""Aggregation-specific errors."""


class CampaignAggregationError(Exception):
    """Base error for deterministic campaign aggregation failures."""


class DuplicateCampaignRowsError(CampaignAggregationError):
    """Raised when scraped rows cannot be joined unambiguously by campaign ID."""
