"""Fail-safe approval-aware workflow notification service."""

import logging
from collections.abc import Callable, Sequence
from datetime import UTC, datetime
from pathlib import Path

from marketing_ops_agent.notifications.errors import NotificationDeliveryError
from marketing_ops_agent.notifications.models import (
    NotificationChannel,
    NotificationPriority,
    NotificationRequest,
    NotificationResult,
    NotificationStatus,
)
from marketing_ops_agent.notifications.providers import (
    DeterministicMockNotificationProvider,
    NotificationProvider,
)
from marketing_ops_agent.observability import sanitize_observability_text

logger = logging.getLogger(__name__)


class NotificationService:
    """Build and send approval-aware workflow summary notifications."""

    def __init__(
        self,
        *,
        provider: NotificationProvider | None = None,
        enabled: bool = True,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        """Initialize the notification service.

        Args:
            provider: Notification provider; the deterministic mock is used
                when omitted.
            enabled: Whether notification delivery should call the provider.
            clock: Optional clock used for deterministic request and status
                timestamps.
        """

        self._provider = provider or DeterministicMockNotificationProvider()
        self._enabled = enabled
        self._clock = clock or (lambda: datetime.now(UTC))

    async def send_report_summary(
        self,
        *,
        run_id: str,
        report_path: Path | str,
        snapshot_count: int,
        finding_count: int,
        critical_finding_count: int,
        human_review_required: bool,
        pending_approval_request_ids: Sequence[str] = (),
    ) -> NotificationResult:
        """Send a deterministic notification for a completed workflow run.

        Args:
            run_id: Workflow run identifier.
            report_path: Local Markdown report path.
            snapshot_count: Number of validated campaign snapshots.
            finding_count: Number of deterministic findings.
            critical_finding_count: Number of critical deterministic findings.
            human_review_required: Whether review is required before sensitive
                follow-up.
            pending_approval_request_ids: Pending approval request IDs to
                reference without treating them as approved actions.

        Returns:
            Notification result. Disabled or failed delivery returns a
            structured result instead of raising.

        Side Effects:
            May call the configured notification provider when enabled.
        """

        if not self._enabled:
            return self._status_result(
                status=NotificationStatus.DISABLED,
                error_message="Notification delivery is disabled.",
            )

        request = build_report_summary_notification_request(
            run_id=run_id,
            report_path=report_path,
            snapshot_count=snapshot_count,
            finding_count=finding_count,
            critical_finding_count=critical_finding_count,
            human_review_required=human_review_required,
            pending_approval_request_ids=pending_approval_request_ids,
            channel=self._provider.channel,
            created_at=self._normalize_datetime(self._clock()),
        )

        try:
            return await self._provider.send(request)
        except NotificationDeliveryError as exc:
            logger.warning("Notification delivery failed: %s", exc)
            return self._status_result(
                status=NotificationStatus.FAILED,
                request=request,
                error_message=str(exc),
            )
        except Exception as exc:
            logger.exception("Unexpected notification delivery failure")
            return self._status_result(
                status=NotificationStatus.FAILED,
                request=request,
                error_message=str(exc),
            )

    def _status_result(
        self,
        *,
        status: NotificationStatus,
        request: NotificationRequest | None = None,
        error_message: str | None = None,
    ) -> NotificationResult:
        """Build a disabled or failed notification result.

        Args:
            status: Disabled or failed result status.
            request: Optional request that failed delivery.
            error_message: Optional failure text to sanitize.

        Returns:
            Structured notification result.
        """

        return NotificationResult(
            status=status,
            channel=self._provider.channel,
            provider=self._provider.provider_name,
            delivered_at=self._normalize_datetime(self._clock()),
            request=request,
            error_message=(
                None
                if error_message is None
                else sanitize_observability_text(error_message)
            ),
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


def build_report_summary_notification_request(
    *,
    run_id: str,
    report_path: Path | str,
    snapshot_count: int,
    finding_count: int,
    critical_finding_count: int,
    human_review_required: bool,
    pending_approval_request_ids: Sequence[str],
    channel: NotificationChannel,
    created_at: datetime,
) -> NotificationRequest:
    """Build the deterministic workflow-completion notification payload.

    Args:
        run_id: Workflow run identifier.
        report_path: Local Markdown report path.
        snapshot_count: Number of validated campaign snapshots.
        finding_count: Number of deterministic findings.
        critical_finding_count: Number of critical deterministic findings.
        human_review_required: Whether review is required before sensitive
            follow-up.
        pending_approval_request_ids: Pending approval IDs to reference.
        channel: Notification channel supplied by the provider.
        created_at: Timezone-aware request creation timestamp.

    Returns:
        Sanitized notification request that does not include report body text,
        raw source payloads, credentials or approved-action claims.
    """

    approval_ids = tuple(pending_approval_request_ids)
    priority = _priority_for_summary(
        critical_finding_count=critical_finding_count,
        human_review_required=human_review_required,
        approval_request_count=len(approval_ids),
        finding_count=finding_count,
    )
    subject = f"Daily marketing report completed: {run_id}"
    message_lines = [
        "Daily marketing report completed.",
        f"Run ID: {run_id}",
        f"Report path: {Path(report_path)}",
        f"Snapshot count: {snapshot_count}",
        f"Finding count: {finding_count}",
        f"Critical finding count: {critical_finding_count}",
        f"Human review required: {_format_bool(human_review_required)}",
        f"Approval request count: {len(approval_ids)}",
    ]
    if approval_ids:
        message_lines.extend(
            [
                "Pending approval request IDs:",
                *[f"- {approval_id}" for approval_id in approval_ids],
                (
                    "Pending approval requests are not approved actions; "
                    "review and approve them before sensitive follow-up."
                ),
            ]
        )
    else:
        message_lines.append("No pending approval requests were created for this run.")
    message_lines.append(
        "This notification is a summary only and does not approve or execute actions."
    )

    return NotificationRequest(
        channel=channel,
        priority=priority,
        subject=subject,
        message="\n".join(message_lines),
        run_id=run_id,
        report_path=Path(report_path),
        snapshot_count=snapshot_count,
        finding_count=finding_count,
        critical_finding_count=critical_finding_count,
        human_review_required=human_review_required,
        approval_request_count=len(approval_ids),
        pending_approval_request_ids=approval_ids,
        created_at=created_at,
        metadata={
            "approval_aware": True,
            "summary_only": True,
            "contains_approved_actions": False,
        },
    )


def _priority_for_summary(
    *,
    critical_finding_count: int,
    human_review_required: bool,
    approval_request_count: int,
    finding_count: int,
) -> NotificationPriority:
    """Choose notification priority from deterministic workflow counts.

    Args:
        critical_finding_count: Number of critical deterministic findings.
        human_review_required: Whether review is required.
        approval_request_count: Number of pending approval requests.
        finding_count: Number of deterministic findings.

    Returns:
        Critical, warning or informational notification priority.
    """

    if critical_finding_count > 0 or human_review_required or approval_request_count > 0:
        return NotificationPriority.CRITICAL
    if finding_count > 0:
        return NotificationPriority.WARNING
    return NotificationPriority.INFO


def _format_bool(value: bool) -> str:
    """Format a boolean value for deterministic notification text.

    Args:
        value: Boolean value to format.

    Returns:
        Lowercase yes/no text.
    """

    return "yes" if value else "no"
