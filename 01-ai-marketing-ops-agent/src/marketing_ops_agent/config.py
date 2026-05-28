"""Configuration loading for local services and clients."""

import os

from pydantic import BaseModel, ConfigDict, Field

from marketing_ops_agent.utils.retry import RetryConfig


class AppConfig(BaseModel):
    """Runtime configuration with safe local defaults."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    marketing_panel_base_url: str = "http://localhost:8000"
    marketing_panel_username: str = ""
    marketing_panel_password: str = ""
    marketing_panel_2fa_code: str = ""
    campaign_api_base_url: str = "http://localhost:8001"
    analytics_graphql_url: str = "http://localhost:8002/graphql"
    project_management_api_base_url: str = "http://localhost:8003"
    request_timeout_seconds: float = Field(default=15.0, gt=0)
    retry_max_attempts: int = Field(default=3, ge=1)

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Load configuration from environment variables."""

        return cls(
            marketing_panel_base_url=os.getenv(
                "MARKETING_PANEL_BASE_URL",
                cls.model_fields["marketing_panel_base_url"].default,
            ),
            marketing_panel_username=os.getenv(
                "MARKETING_PANEL_USERNAME",
                cls.model_fields["marketing_panel_username"].default,
            ),
            marketing_panel_password=os.getenv(
                "MARKETING_PANEL_PASSWORD",
                cls.model_fields["marketing_panel_password"].default,
            ),
            marketing_panel_2fa_code=os.getenv(
                "MARKETING_PANEL_2FA_CODE",
                cls.model_fields["marketing_panel_2fa_code"].default,
            ),
            campaign_api_base_url=os.getenv(
                "CAMPAIGN_API_BASE_URL",
                cls.model_fields["campaign_api_base_url"].default,
            ),
            analytics_graphql_url=os.getenv(
                "ANALYTICS_GRAPHQL_URL",
                cls.model_fields["analytics_graphql_url"].default,
            ),
            project_management_api_base_url=os.getenv(
                "PROJECT_MANAGEMENT_API_BASE_URL",
                cls.model_fields["project_management_api_base_url"].default,
            ),
            request_timeout_seconds=_get_float_env("REQUEST_TIMEOUT_SECONDS", 15.0),
            retry_max_attempts=_get_int_env("RETRY_MAX_ATTEMPTS", 3),
        )

    def retry_config(self) -> RetryConfig:
        """Build retry configuration from runtime settings."""

        return RetryConfig(max_attempts=self.retry_max_attempts)


def load_config() -> AppConfig:
    """Load the default application configuration."""

    return AppConfig.from_env()


def _get_float_env(name: str, default: float) -> float:
    raw_value = os.getenv(name)
    if raw_value is None or raw_value == "":
        return default
    try:
        return float(raw_value)
    except ValueError as exc:
        raise ValueError(f"{name} must be a valid float") from exc


def _get_int_env(name: str, default: int) -> int:
    raw_value = os.getenv(name)
    if raw_value is None or raw_value == "":
        return default
    try:
        return int(raw_value)
    except ValueError as exc:
        raise ValueError(f"{name} must be a valid integer") from exc
