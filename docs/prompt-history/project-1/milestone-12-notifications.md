# Milestone 12 - Approval-Aware Notifications

Curated reconstruction based on the implemented milestone.

## Purpose

Add optional notification delivery that is deterministic, approval-aware and
safe for local demos and tests.

## Prompt Used

```text
Continue Project 1: 01-ai-marketing-ops-agent.

Milestone 12: implement approval-aware notification delivery.

Goal:
Add optional, deterministic, approval-aware notification delivery.

Implement:
- NotificationRequest
- NotificationResult
- NotificationStatus
- NotificationChannel
- NotificationPriority if useful
- NotificationProvider abstraction
- DeterministicMockNotificationProvider
- NotificationService
- optional workflow integration and configuration toggle
- optional run-history notification status/count fields
- tests for mock delivery, disabled mode, approval-aware content, secret safety and fail-safe workflow continuation

Constraints:
- Do not call real Slack, Telegram, email or external notification APIs in tests.
- Do not hardcode notification credentials.
- Pending approval requests are not approved actions.
- Do not send sensitive action recommendations as approved work.
- Workflow should continue when notification delivery fails.

After implementation, summarize models, provider abstraction, service behavior, workflow integration, tests and configuration.
```

## Expected Verification

```text
uv run pytest
uv run ruff check .
uv run mypy src
```

## Result Summary

Implemented optional summary-only notification delivery through a deterministic
mock provider. Notifications include workflow counts, report path, run ID and
pending approval request IDs when present, while explicitly avoiding approved
action claims.

Verified status from the handoff:

```text
105 tests passed
ruff clean
mypy clean
```

