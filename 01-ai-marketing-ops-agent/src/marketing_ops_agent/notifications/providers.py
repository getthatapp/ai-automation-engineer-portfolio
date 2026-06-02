"""Notification provider abstraction and deterministic mock provider."""

from collections.abc import Callable
from datetime import UTC, datetime
from typing import Protocol

from marketing_ops_agent.notifications.models import (
    NotificationChannel,
    NotificationRequest,
    NotificationResult,
    NotificationStatus,
)


class NotificationProvider(Protocol):
    """Provider contract for workflow notification delivery."""

    @property
    def provider_name(self) -> str:
        """Human-readable provider name."""

    @property
    def channel(self) -> NotificationChannel:
        """Notification channel implemented by the provider."""

    async def send(self, request: NotificationRequest) -> NotificationResult:
        """Send a prepared notification request.

        Args:
            request: Validated notification payload.

        Returns:
            Delivery result from the provider.
        """


class DeterministicMockNotificationProvider:
    """In-memory notification provider for tests and local demos."""

    def __init__(
        self,
        *,
        provider_name: str = "mock",
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        """Initialize the deterministic mock provider.

        Args:
            provider_name: Provider label returned in notification results.
            clock: Optional clock used for deterministic result timestamps.
        """

        self._provider_name = provider_name
        self._clock = clock or (lambda: datetime.now(UTC))
        self.deliveries: list[NotificationRequest] = []

    @property
    def provider_name(self) -> str:
        """Return the provider label used in notification results."""

        return self._provider_name

    @property
    def channel(self) -> NotificationChannel:
        """Return the mock notification channel."""

        return NotificationChannel.MOCK

    async def send(self, request: NotificationRequest) -> NotificationResult:
        """Record the notification request without calling external APIs.

        Args:
            request: Validated notification payload.

        Returns:
            Deterministic sent result containing a local mock notification ID.

        Side Effects:
            Appends the request to the provider's in-memory delivery list.
        """

        self.deliveries.append(request)
        return NotificationResult(
            status=NotificationStatus.SENT,
            channel=self.channel,
            provider=self.provider_name,
            delivered_at=self._normalize_datetime(self._clock()),
            request=request,
            notification_id=f"mock-notification-{len(self.deliveries):03d}",
        )

    @staticmethod
    def _normalize_datetime(value: datetime) -> datetime:
        """Normalize a datetime to UTC, treating naive values as UTC.

        Args:
            value: Datetime to normalize.

        Returns:
            Timezone-aware UTC datetime.
        """

        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)
