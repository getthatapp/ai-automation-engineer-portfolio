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
    llm_interpretation_enabled: bool = False
    llm_provider: str = "mock"
    llm_model: str = "deterministic-marketing-interpreter"
    notification_delivery_enabled: bool = False
    notification_provider: str = "mock"
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
            llm_interpretation_enabled=_get_bool_env(
                "LLM_INTERPRETATION_ENABLED",
                False,
            ),
            llm_provider=os.getenv(
                "LLM_PROVIDER",
                cls.model_fields["llm_provider"].default,
            ),
            llm_model=os.getenv(
                "LLM_MODEL",
                cls.model_fields["llm_model"].default,
            ),
            notification_delivery_enabled=_get_bool_env(
                "NOTIFICATION_DELIVERY_ENABLED",
                False,
            ),
            notification_provider=os.getenv(
                "NOTIFICATION_PROVIDER",
                cls.model_fields["notification_provider"].default,
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
    """Read a float environment variable with validation.

    Args:
        name: Environment variable name.
        default: Value returned when the variable is unset or empty.

    Returns:
        Parsed float value.

    Raises:
        ValueError: If the environment value is not a valid float.
    """
    raw_value = os.getenv(name)
    if raw_value is None or raw_value == "":
        return default
    try:
        return float(raw_value)
    except ValueError as exc:
        raise ValueError(f"{name} must be a valid float") from exc


def _get_int_env(name: str, default: int) -> int:
    """Read an integer environment variable with validation.

    Args:
        name: Environment variable name.
        default: Value returned when the variable is unset or empty.

    Returns:
        Parsed integer value.

    Raises:
        ValueError: If the environment value is not a valid integer.
    """
    raw_value = os.getenv(name)
    if raw_value is None or raw_value == "":
        return default
    try:
        return int(raw_value)
    except ValueError as exc:
        raise ValueError(f"{name} must be a valid integer") from exc


def _get_bool_env(name: str, default: bool) -> bool:
    """Read a boolean environment variable with validation.

    Args:
        name: Environment variable name.
        default: Value returned when the variable is unset or empty.

    Returns:
        Parsed boolean value.

    Raises:
        ValueError: If the environment value is not a recognized boolean.
    """
    raw_value = os.getenv(name)
    if raw_value is None or raw_value == "":
        return default
    normalized = raw_value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"{name} must be a valid boolean")
