"""Typed service clients for local mock integrations."""

from marketing_ops_agent.clients.analytics_client import AnalyticsCampaignMetrics, AnalyticsClient
from marketing_ops_agent.clients.campaign_client import CampaignClient, CampaignSummary
from marketing_ops_agent.clients.errors import (
    GraphQLResponseError,
    RetryableServiceResponseError,
    ServiceClientError,
    ServiceConnectionError,
    ServiceDecodeError,
    ServiceResponseError,
    ServiceTimeoutError,
)
from marketing_ops_agent.clients.project_management_client import (
    ProjectManagementClient,
    ProjectTask,
    ProjectTaskCreate,
)

__all__ = [
    "AnalyticsCampaignMetrics",
    "AnalyticsClient",
    "CampaignClient",
    "CampaignSummary",
    "GraphQLResponseError",
    "ProjectManagementClient",
    "ProjectTask",
    "ProjectTaskCreate",
    "RetryableServiceResponseError",
    "ServiceClientError",
    "ServiceConnectionError",
    "ServiceDecodeError",
    "ServiceResponseError",
    "ServiceTimeoutError",
]
