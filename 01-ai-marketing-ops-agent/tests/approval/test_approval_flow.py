from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path

import pytest

from marketing_ops_agent.aggregation import CampaignSnapshot
from marketing_ops_agent.anomaly import AnomalyFinding, AnomalySeverity, AnomalyType
from marketing_ops_agent.approval import (
    ApprovalDecision,
    ApprovalRiskLevel,
    ApprovalService,
    ApprovalSource,
    ApprovalStatus,
    LocalApprovalStore,
    MalformedApprovalRecordLineError,
)
from marketing_ops_agent.approval.models import ApprovalRequest
from marketing_ops_agent.browser import ScrapedCampaignRow
from marketing_ops_agent.clients.analytics_client import AnalyticsCampaignMetrics
from marketing_ops_agent.llm import (
    LLMActionPriority,
    LLMInterpretationResult,
    LLMInterpretationStatus,
    LLMRecommendedAction,
)
from marketing_ops_agent.models import Campaign, CampaignMetrics, Channel, WorkflowStatus
from marketing_ops_agent.reporting import ReportMetadata
from marketing_ops_agent.workflows import DailyMarketingReportWorkflow

REFERENCE_TIME = datetime(2026, 5, 28, 12, 0, tzinfo=UTC)


class FakeScraper:
    """Fake panel scraper for workflow approval tests."""

    def __init__(self, rows: Sequence[ScrapedCampaignRow]) -> None:
        """Store rows returned by the fake scraper.

        Args:
            rows: Scraped rows to return.
        """

        self._rows = list(rows)

    async def scrape_campaign_rows(self) -> list[ScrapedCampaignRow]:
        """Return configured scraped rows."""

        return self._rows


class FakeCampaignClient:
    """Fake Campaign REST client for workflow approval tests."""

    def __init__(self, campaigns: Mapping[str, Campaign]) -> None:
        """Store campaigns returned by the fake client.

        Args:
            campaigns: Mapping from campaign ID to campaign model.
        """

        self._campaigns = campaigns

    async def get_campaign(self, campaign_id: str) -> Campaign:
        """Return a campaign by ID."""

        return self._campaigns[campaign_id]


class FakeAnalyticsClient:
    """Fake Analytics GraphQL client for workflow approval tests."""

    def __init__(self, metrics: Mapping[str, AnalyticsCampaignMetrics]) -> None:
        """Store metrics returned by the fake client.

        Args:
            metrics: Mapping from campaign ID to analytics metrics.
        """

        self._metrics = metrics

    async def get_campaign_metrics(self, campaign_id: str) -> AnalyticsCampaignMetrics:
        """Return analytics metrics by campaign ID."""

        return self._metrics[campaign_id]


class FakeDetector:
    """Fake anomaly detector for workflow approval tests."""

    def __init__(self, findings: Sequence[AnomalyFinding]) -> None:
        """Store findings returned by the fake detector."""

        self._findings = list(findings)

    def detect(self, snapshots: Sequence[CampaignSnapshot]) -> list[AnomalyFinding]:
        """Return configured deterministic findings."""

        return self._findings


class FakeReportWriter:
    """Fake deterministic report writer for workflow approval tests."""

    def write(
        self,
        snapshots: Sequence[CampaignSnapshot],
        findings: Sequence[AnomalyFinding],
        metadata: ReportMetadata | None = None,
    ) -> str:
        """Return stable Markdown report text."""

        return "# deterministic report\n"


def test_creating_approval_request_persists_pending_record(tmp_path: Path) -> None:
    store = _store(tmp_path)
    request = _approval_request()

    created = store.create(request)

    assert created == request
    assert store.get(request.approval_id) == request
    assert store.list_pending() == [request]
    assert (tmp_path / "approvals.jsonl").exists()


def test_listing_pending_and_all_approvals(tmp_path: Path) -> None:
    store = _store(tmp_path)
    first = store.create(_approval_request(approval_id="approval-first"))
    second = store.create(_approval_request(approval_id="approval-second"))
    approved = store.approve(first.approval_id, decided_by="manager@example.com")

    assert store.list_pending() == [second]
    assert store.list_all() == [approved, second]


def test_getting_approval_by_id(tmp_path: Path) -> None:
    store = _store(tmp_path)
    request = store.create(_approval_request())

    assert store.get(request.approval_id) == request
    assert store.get("missing") is None


def test_approving_request_records_decision(tmp_path: Path) -> None:
    store = _store(tmp_path)
    request = store.create(_approval_request())

    approved = store.approve(
        request.approval_id,
        decided_by="manager@example.com",
        reason="Evidence reviewed.",
    )

    assert approved.status is ApprovalStatus.APPROVED
    assert isinstance(approved.decision, ApprovalDecision)
    assert approved.decision.status is ApprovalStatus.APPROVED
    assert approved.decision.decided_at == REFERENCE_TIME
    assert approved.decision.decided_by == "manager@example.com"
    assert store.list_pending() == []


def test_rejecting_request_records_decision(tmp_path: Path) -> None:
    store = _store(tmp_path)
    request = store.create(_approval_request())

    rejected = store.reject(
        request.approval_id,
        decided_by="manager@example.com",
        reason="Needs more data.",
    )

    assert rejected.status is ApprovalStatus.REJECTED
    assert rejected.decision is not None
    assert rejected.decision.status is ApprovalStatus.REJECTED
    assert rejected.decision.reason == "Needs more data."


def test_duplicate_request_handling_is_idempotent(tmp_path: Path) -> None:
    store = _store(tmp_path)
    request = _approval_request()

    first = store.create(request)
    second = store.create(request.model_copy(update={"title": "Changed"}))

    assert first == second
    assert store.list_all() == [request]


def test_critical_finding_creates_approval_request(tmp_path: Path) -> None:
    store = _store(tmp_path)
    service = _service(store)

    requests = service.create_requests_for_run(
        run_id="run-001",
        findings=[
            _finding(
                severity=AnomalySeverity.CRITICAL,
                requires_human_review=False,
            )
        ],
    )

    assert len(requests) == 1
    request = requests[0]
    assert request.status is ApprovalStatus.PENDING
    assert request.risk_level is ApprovalRiskLevel.HIGH
    assert request.source is ApprovalSource.DETERMINISTIC_FINDING
    assert request.run_id == "run-001"
    assert request.campaign_id == "cmp-search-brand"


def test_human_review_finding_creates_approval_request(tmp_path: Path) -> None:
    store = _store(tmp_path)
    service = _service(store)

    requests = service.create_requests_for_run(
        run_id="run-001",
        findings=[
            _finding(
                severity=AnomalySeverity.WARNING,
                requires_human_review=True,
            )
        ],
    )

    assert len(requests) == 1
    assert requests[0].risk_level is ApprovalRiskLevel.MEDIUM
    assert requests[0].status is ApprovalStatus.PENDING


@pytest.mark.asyncio
async def test_healthy_workflow_creates_no_approval_request(tmp_path: Path) -> None:
    store = _store(tmp_path)
    workflow = _workflow(
        findings=[],
        approval_service=_service(store),
        reports_dir=tmp_path / "reports",
    )

    result = await workflow.run()

    assert result.status is WorkflowStatus.SUCCEEDED
    assert result.approval_request_ids == ()
    assert store.list_all() == []


def test_high_risk_llm_recommendation_creates_approval_request(
    tmp_path: Path,
) -> None:
    store = _store(tmp_path)
    service = _service(store)
    llm_result = LLMInterpretationResult(
        status=LLMInterpretationStatus.SUCCEEDED,
        provider="mock",
        model="deterministic",
        generated_at=REFERENCE_TIME,
        source_campaign_count=1,
        source_finding_count=0,
        recommendations=(
            LLMRecommendedAction(
                title="Pause high-risk campaign",
                rationale="LLM recommends pausing due to deterministic evidence.",
                priority=LLMActionPriority.HIGH,
                campaign_id="cmp-search-brand",
                source_anomaly_types=("negative_roi",),
                requires_human_approval=True,
            ),
        ),
    )

    requests = service.create_requests_for_run(
        run_id="run-001",
        findings=[],
        llm_interpretation=llm_result,
    )

    assert len(requests) == 1
    assert requests[0].source is ApprovalSource.LLM_RECOMMENDATION
    assert requests[0].risk_level is ApprovalRiskLevel.HIGH
    assert requests[0].status is ApprovalStatus.PENDING


def test_no_secrets_are_persisted(tmp_path: Path) -> None:
    store = _store(tmp_path)
    request = _approval_request(
        title="Review password=super-secret",
        rationale="Token token=abc123 must be redacted.",
        source_evidence={"authorization": "Bearer secret-token"},
    )

    store.create(request)

    persisted = (tmp_path / "approvals.jsonl").read_text(encoding="utf-8")
    assert "super-secret" not in persisted
    assert "abc123" not in persisted
    assert "secret-token" not in persisted
    assert "[REDACTED]" in persisted


def test_malformed_approval_persistence_handling(tmp_path: Path) -> None:
    path = tmp_path / "approvals.jsonl"
    path.write_text("{not-json}\n", encoding="utf-8")
    store = LocalApprovalStore(path, clock=lambda: REFERENCE_TIME)

    with pytest.raises(MalformedApprovalRecordLineError):
        store.list_all()


def _store(tmp_path: Path) -> LocalApprovalStore:
    return LocalApprovalStore(tmp_path / "approvals.jsonl", clock=lambda: REFERENCE_TIME)


def _service(store: LocalApprovalStore) -> ApprovalService:
    return ApprovalService(store=store, clock=lambda: REFERENCE_TIME)


def _approval_request(
    *,
    approval_id: str = "approval-001",
    title: str = "Review critical finding",
    rationale: str = "Critical deterministic finding requires human approval.",
    source_evidence: dict[str, str | int | float | bool | None] | None = None,
) -> ApprovalRequest:
    return ApprovalRequest(
        approval_id=approval_id,
        run_id="run-001",
        campaign_id="cmp-search-brand",
        source=ApprovalSource.DETERMINISTIC_FINDING,
        source_reference=AnomalyType.NEGATIVE_ROI.value,
        risk_level=ApprovalRiskLevel.HIGH,
        title=title,
        rationale=rationale,
        source_evidence=source_evidence or {"panel_roi": -0.2},
        created_at=REFERENCE_TIME,
    )


def _finding(
    *,
    severity: AnomalySeverity,
    requires_human_review: bool,
) -> AnomalyFinding:
    return AnomalyFinding(
        campaign_id="cmp-search-brand",
        anomaly_type=AnomalyType.NEGATIVE_ROI,
        severity=severity,
        message="Campaign ROI is below threshold.",
        source="deterministic_anomaly_detector",
        source_evidence={"panel_roi": -0.2},
        requires_human_review=requires_human_review,
    )


def _workflow(
    *,
    findings: Sequence[AnomalyFinding],
    approval_service: ApprovalService,
    reports_dir: Path,
) -> DailyMarketingReportWorkflow:
    row = _row()
    return DailyMarketingReportWorkflow(
        scraper=FakeScraper([row]),
        campaign_client=FakeCampaignClient({row.campaign_id: _campaign()}),
        analytics_client=FakeAnalyticsClient({row.campaign_id: _analytics()}),
        detector=FakeDetector(findings),
        report_writer=FakeReportWriter(),
        approval_service=approval_service,
        reports_dir=reports_dir,
        clock=lambda: REFERENCE_TIME,
    )


def _row() -> ScrapedCampaignRow:
    return ScrapedCampaignRow(
        campaign_id="cmp-search-brand",
        name="Brand Search Defense",
        channel=Channel.SEARCH,
        impressions=120_000,
        clicks=8_200,
        conversions=640,
        cost=12_150.0,
        revenue=38_400.0,
    )


def _campaign() -> Campaign:
    return Campaign(
        campaign_id="cmp-search-brand",
        name="Brand Search Defense",
        channel=Channel.SEARCH,
        metrics=CampaignMetrics(
            impressions=120_000,
            clicks=8_200,
            conversions=640,
            spend=12_150.0,
            revenue=38_400.0,
        ),
        collected_at=REFERENCE_TIME,
    )


def _analytics() -> AnalyticsCampaignMetrics:
    return AnalyticsCampaignMetrics(
        campaignId="cmp-search-brand",
        impressions=120_000,
        clicks=8_200,
        conversions=640,
        revenue=38_400.0,
        cost=12_150.0,
    )
