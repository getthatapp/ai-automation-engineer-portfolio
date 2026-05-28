from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from marketing_ops_agent.models import (
    Campaign,
    CampaignMetrics,
    Channel,
    WorkflowRunLog,
    WorkflowStatus,
)


def test_campaign_metrics_calculate_rates() -> None:
    metrics = CampaignMetrics(
        impressions=1_000,
        clicks=100,
        conversions=10,
        spend=50.0,
        revenue=250.0,
    )

    assert metrics.ctr == 0.1
    assert metrics.conversion_rate == 0.1
    assert metrics.return_on_ad_spend == 5.0


def test_campaign_rejects_blank_required_text() -> None:
    with pytest.raises(ValidationError):
        Campaign(
            campaign_id="  ",
            name="Spring Launch",
            channel=Channel.SEARCH,
            metrics=CampaignMetrics(
                impressions=10,
                clicks=1,
                conversions=0,
                spend=1.0,
                revenue=0.0,
            ),
            collected_at=datetime.now(UTC),
        )


def test_workflow_run_log_defaults_are_auditable() -> None:
    run_log = WorkflowRunLog(
        run_id="run-001",
        status=WorkflowStatus.PENDING,
        started_at=datetime.now(UTC),
    )

    assert run_log.campaigns_processed == 0
    assert run_log.retry_count == 0
    assert run_log.finished_at is None
