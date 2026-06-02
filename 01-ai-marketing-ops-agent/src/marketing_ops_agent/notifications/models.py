"""Typed models for approval-aware notification delivery."""

from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from marketing_ops_agent.observability import sanitize_observability_text


class NotificationStatus(StrEnum):
    """Lifecycle status for an optional notification attempt."""

    DISABLED = "disabled"
    SENT = "sent"
    FAILED = "failed"


class NotificationChannel(StrEnum):
    """Notification destination category."""

    MOCK = "mock"
    SLACK = "slack"
    TELEGRAM = "telegram"
    EMAIL = "email"


class NotificationPriority(StrEnum):
    """Business priority used to route or label a notification."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


NotificationMetadataValue = str | int | bool


class NotificationRequest(BaseModel):
    """Validated notification payload for a completed workflow summary."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    channel: NotificationChannel = NotificationChannel.MOCK
    priority: NotificationPriority = NotificationPriority.INFO
    subject: str = Field(min_length=1, max_length=300)
    message: str = Field(min_length=1, max_length=4_000)
    run_id: str = Field(min_length=1)
    report_path: Path
    snapshot_count: int = Field(ge=0)
    finding_count: int = Field(ge=0)
    critical_finding_count: int = Field(ge=0)
    human_review_required: bool
    approval_request_count: int = Field(ge=0)
    pending_approval_request_ids: tuple[str, ...] = ()
    created_at: datetime
    metadata: dict[str, NotificationMetadataValue] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_approval_count(self) -> "NotificationRequest":
        """Ensure the approval count matches the explicit pending ID list.

        Returns:
            Validated notification request.

        Raises:
            ValueError: If the approval count disagrees with the pending ID
                tuple length.
        """

        if self.approval_request_count != len(self.pending_approval_request_ids):
            raise ValueError(
                "approval_request_count must match pending_approval_request_ids"
            )
        return self

    @field_validator("subject", "message", "run_id")
    @classmethod
    def sanitize_required_text(cls, value: str) -> str:
        """Trim and redact required notification text fields.

        Args:
            value: Raw text value.

        Returns:
            Sanitized non-empty text.

        Raises:
            ValueError: If the text is blank after trimming.
        """

        sanitized = sanitize_observability_text(value.strip())
        if not sanitized:
            raise ValueError("notification text fields must not be blank")
        return sanitized

    @field_validator("pending_approval_request_ids")
    @classmethod
    def sanitize_pending_approval_ids(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        """Trim and redact pending approval request IDs.

        Args:
            value: Raw approval request IDs.

        Returns:
            Sanitized approval request IDs.

        Raises:
            ValueError: If any ID is blank after trimming.
        """

        sanitized_ids = tuple(sanitize_observability_text(item.strip()) for item in value)
        if any(not item for item in sanitized_ids):
            raise ValueError("pending approval request IDs must not be blank")
        return sanitized_ids

    @field_validator("report_path", mode="before")
    @classmethod
    def sanitize_report_path(cls, value: object) -> Path:
        """Redact secret-like text from report paths included in notifications.

        Args:
            value: Raw path-like value.

        Returns:
            Sanitized report path.

        Raises:
            ValueError: If the path is blank after trimming.
        """

        sanitized = sanitize_observability_text(str(value).strip())
        if not sanitized:
            raise ValueError("report_path must not be blank")
        return Path(sanitized)

    @field_validator("created_at")
    @classmethod
    def normalize_created_at(cls, value: datetime) -> datetime:
        """Normalize notification creation timestamps to UTC.

        Args:
            value: Timezone-aware creation timestamp.

        Returns:
            UTC-normalized timestamp.

        Raises:
            ValueError: If the timestamp is naive.
        """

        if value.tzinfo is None:
            raise ValueError("created_at must be timezone-aware")
        return value.astimezone(UTC)

    @field_validator("metadata")
    @classmethod
    def sanitize_metadata(
        cls,
        value: dict[str, NotificationMetadataValue],
    ) -> dict[str, NotificationMetadataValue]:
        """Normalize and redact notification metadata.

        Args:
            value: Raw metadata mapping.

        Returns:
            Sorted metadata with blank keys removed and string values redacted.
        """

        sanitized: dict[str, NotificationMetadataValue] = {}
        for key, item in sorted(value.items()):
            stripped_key = sanitize_observability_text(str(key).strip())
            if not stripped_key:
                continue
            sanitized[stripped_key] = (
                sanitize_observability_text(item.strip())
                if isinstance(item, str)
                else item
            )
        return sanitized


class NotificationResult(BaseModel):
    """Result of an optional notification delivery attempt."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    status: NotificationStatus
    channel: NotificationChannel
    provider: str = Field(min_length=1)
    delivered_at: datetime
    request: NotificationRequest | None = None
    notification_id: str | None = None
    error_message: str | None = None

    @field_validator("provider", "notification_id", "error_message")
    @classmethod
    def sanitize_optional_text(cls, value: str | None) -> str | None:
        """Trim and redact optional result text fields.

        Args:
            value: Optional raw text.

        Returns:
            Sanitized text, or `None` when blank.
        """

        if value is None:
            return None
        sanitized = sanitize_observability_text(value.strip())
        return sanitized or None

    @field_validator("delivered_at")
    @classmethod
    def normalize_delivered_at(cls, value: datetime) -> datetime:
        """Normalize notification result timestamps to UTC.

        Args:
            value: Timezone-aware delivery timestamp.

        Returns:
            UTC-normalized timestamp.

        Raises:
            ValueError: If the timestamp is naive.
        """

        if value.tzinfo is None:
            raise ValueError("delivered_at must be timezone-aware")
        return value.astimezone(UTC)
