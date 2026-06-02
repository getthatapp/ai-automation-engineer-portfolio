from datetime import UTC, datetime
from pathlib import Path

import pytest

from marketing_ops_agent.notifications import (
    DeterministicMockNotificationProvider,
    NotificationService,
    NotificationStatus,
)

REFERENCE_TIME = datetime(2026, 5, 28, 12, 0, tzinfo=UTC)


@pytest.mark.asyncio
async def test_mock_provider_records_delivery() -> None:
    """Verify the mock provider stores sent notification requests."""

    provider = DeterministicMockNotificationProvider(clock=lambda: REFERENCE_TIME)
    service = NotificationService(provider=provider, clock=lambda: REFERENCE_TIME)

    result = await service.send_report_summary(
        run_id="daily-marketing-report-20260528T120000Z",
        report_path=Path("reports/daily-marketing-report-20260528T120000Z.md"),
        snapshot_count=3,
        finding_count=2,
        critical_finding_count=1,
        human_review_required=True,
        pending_approval_request_ids=("approval-001", "approval-002"),
    )

    assert result.status is NotificationStatus.SENT
    assert result.notification_id == "mock-notification-001"
    assert len(provider.deliveries) == 1
    assert provider.deliveries[0] == result.request


@pytest.mark.asyncio
async def test_disabled_notification_mode_does_not_call_provider() -> None:
    """Verify disabled notification mode returns a result without delivery."""

    provider = DeterministicMockNotificationProvider(clock=lambda: REFERENCE_TIME)
    service = NotificationService(
        provider=provider,
        enabled=False,
        clock=lambda: REFERENCE_TIME,
    )

    result = await service.send_report_summary(
        run_id="run-001",
        report_path=Path("reports/run-001.md"),
        snapshot_count=1,
        finding_count=0,
        critical_finding_count=0,
        human_review_required=False,
    )

    assert result.status is NotificationStatus.DISABLED
    assert result.request is None
    assert provider.deliveries == []


@pytest.mark.asyncio
async def test_approval_aware_message_includes_pending_ids_without_approval_claims() -> None:
    """Verify pending approval IDs are referenced without approval claims."""

    service = NotificationService(clock=lambda: REFERENCE_TIME)

    result = await service.send_report_summary(
        run_id="run-needs-review",
        report_path=Path("reports/run-needs-review.md"),
        snapshot_count=2,
        finding_count=4,
        critical_finding_count=1,
        human_review_required=True,
        pending_approval_request_ids=("approval-high-risk-001",),
    )

    assert result.request is not None
    message = result.request.message
    assert "Approval request count: 1" in message
    assert "approval-high-risk-001" in message
    assert "Pending approval requests are not approved actions" in message
    assert "This notification is a summary only" in message
    assert "Approved actions:" not in message
    assert "approved work" not in message


@pytest.mark.asyncio
async def test_healthy_run_sends_simple_report_summary() -> None:
    """Verify a healthy run notification contains only summary metadata."""

    service = NotificationService(clock=lambda: REFERENCE_TIME)

    result = await service.send_report_summary(
        run_id="run-healthy",
        report_path=Path("reports/run-healthy.md"),
        snapshot_count=5,
        finding_count=0,
        critical_finding_count=0,
        human_review_required=False,
    )

    assert result.status is NotificationStatus.SENT
    assert result.request is not None
    assert result.request.snapshot_count == 5
    assert result.request.finding_count == 0
    assert result.request.critical_finding_count == 0
    assert result.request.human_review_required is False
    assert result.request.pending_approval_request_ids == ()
    assert "No pending approval requests" in result.request.message


@pytest.mark.asyncio
async def test_notification_payload_redacts_secret_like_values() -> None:
    """Verify notification payloads redact common inline secret shapes."""

    service = NotificationService(clock=lambda: REFERENCE_TIME)

    result = await service.send_report_summary(
        run_id="run token=abc123",
        report_path=Path("reports/password=local-password.md"),
        snapshot_count=1,
        finding_count=1,
        critical_finding_count=0,
        human_review_required=True,
        pending_approval_request_ids=("approval password=super-secret",),
    )

    payload = result.model_dump_json()
    assert "abc123" not in payload
    assert "super-secret" not in payload
    assert "[REDACTED]" in payload
