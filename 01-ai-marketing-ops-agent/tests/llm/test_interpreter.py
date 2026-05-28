from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path

import pytest

from marketing_ops_agent.aggregation import CampaignSnapshot, DataQualityFlag
from marketing_ops_agent.anomaly import AnomalyFinding, AnomalySeverity, AnomalyType
from marketing_ops_agent.browser import ScrapedCampaignRow
from marketing_ops_agent.clients.analytics_client import AnalyticsCampaignMetrics
from marketing_ops_agent.llm import (
    DeterministicMockLLMProvider,
    LLMInterpretationRequest,
    LLMInterpretationStatus,
    LLMInterpreter,
    build_interpretation_prompt,
)
from marketing_ops_agent.models import Campaign, CampaignMetrics, Channel, WorkflowStatus
from marketing_ops_agent.reporting import ReportMetadata
from marketing_ops_agent.workflows import DailyMarketingReportWorkflow

REFERENCE_TIME = datetime(2026, 5, 28, 12, 0, tzinfo=UTC)


class FakeScraper:
    def __init__(self, rows: Sequence[ScrapedCampaignRow]) -> None:
        self._rows = list(rows)

    async def scrape_campaign_rows(self) -> list[ScrapedCampaignRow]:
        return self._rows


class FakeCampaignClient:
    def __init__(self, campaigns: Mapping[str, Campaign]) -> None:
        self._campaigns = campaigns

    async def get_campaign(self, campaign_id: str) -> Campaign:
        return self._campaigns[campaign_id]


class FakeAnalyticsClient:
    def __init__(self, metrics: Mapping[str, AnalyticsCampaignMetrics]) -> None:
        self._metrics = metrics

    async def get_campaign_metrics(self, campaign_id: str) -> AnalyticsCampaignMetrics:
        return self._metrics[campaign_id]


class FakeDetector:
    def detect(self, snapshots: Sequence[CampaignSnapshot]) -> list[AnomalyFinding]:
        return []


class FakeReportWriter:
    def write(
        self,
        snapshots: Sequence[CampaignSnapshot],
        findings: Sequence[AnomalyFinding],
        metadata: ReportMetadata | None = None,
    ) -> str:
        return "# deterministic report\n\n- no deterministic findings.\n"


@pytest.mark.asyncio
async def test_mock_provider_returns_structured_interpretation() -> None:
    request = _request(findings=[_finding()])
    interpreter = LLMInterpreter(provider=DeterministicMockLLMProvider())

    result = await interpreter.interpret(request)

    assert result.status is LLMInterpretationStatus.SUCCEEDED
    assert result.provider == "mock"
    assert result.source_campaign_count == 1
    assert result.source_finding_count == 1
    assert "Processed 1 validated campaign snapshots" in result.summary
    assert len(result.facts) == 3
    assert result.recommendations[0].campaign_id == "cmp-search-brand"


def test_prompt_does_not_include_raw_credentials_or_secrets() -> None:
    request = _request(
        deterministic_report_summary=(
            "Failure included password=super-secret token=abc123 "
            "authorization=Bearer secret-token"
        ),
        findings=[
            _finding(
                message="Investigate source note password=another-secret",
                source_evidence={"api_key": "api_key=hidden-key"},
            )
        ],
    )

    prompt = build_interpretation_prompt(request)

    assert "super-secret" not in prompt
    assert "abc123" not in prompt
    assert "secret-token" not in prompt
    assert "another-secret" not in prompt
    assert "hidden-key" not in prompt
    assert "[REDACTED]" in prompt


def test_prompt_includes_anti_hallucination_rules() -> None:
    prompt = build_interpretation_prompt(_request())

    assert "Never invent missing metrics" in prompt
    assert "Preserve data quality flags exactly" in prompt
    assert "Keep deterministic facts separate from recommendations" in prompt
    assert "Do not overwrite, suppress or recalculate deterministic anomaly findings" in prompt


def test_prompt_preserves_missing_data_and_quality_flags() -> None:
    request = _request(snapshots=[_snapshot_missing_analytics()])

    prompt = build_interpretation_prompt(request)

    assert '"analytics_metrics": "missing"' in prompt
    assert "missing_analytics_metrics" in prompt
    assert '"requires_human_review": true' in prompt


@pytest.mark.asyncio
async def test_interpreter_does_not_overwrite_deterministic_findings() -> None:
    finding = _finding()
    request = _request(findings=[finding])
    interpreter = LLMInterpreter(provider=DeterministicMockLLMProvider())

    result = await interpreter.interpret(request)

    assert request.findings == (finding,)
    assert result.source_finding_count == 1
    assert result.recommendations[0].source_anomaly_types == (
        AnomalyType.NEGATIVE_ROI.value,
    )


@pytest.mark.asyncio
async def test_llm_disabled_mode_does_not_break_workflow(tmp_path: Path) -> None:
    row = _row()
    workflow = DailyMarketingReportWorkflow(
        scraper=FakeScraper([row]),
        campaign_client=FakeCampaignClient({row.campaign_id: _campaign()}),
        analytics_client=FakeAnalyticsClient({row.campaign_id: _analytics()}),
        detector=FakeDetector(),
        report_writer=FakeReportWriter(),
        llm_interpreter=LLMInterpreter(
            provider=DeterministicMockLLMProvider(),
            enabled=False,
            clock=lambda: REFERENCE_TIME,
        ),
        reports_dir=tmp_path,
        clock=lambda: REFERENCE_TIME,
    )

    result = await workflow.run()

    assert result.status is WorkflowStatus.SUCCEEDED
    assert result.report_path.exists()
    assert result.llm_interpretation is not None
    assert result.llm_interpretation.status is LLMInterpretationStatus.DISABLED


@pytest.mark.asyncio
async def test_token_usage_is_captured_when_provider_returns_it() -> None:
    interpreter = LLMInterpreter(
        provider=DeterministicMockLLMProvider(include_token_usage=True),
    )

    result = await interpreter.interpret(_request(findings=[_finding()]))

    assert result.token_usage is not None
    assert result.token_usage.prompt_tokens > 0
    assert result.token_usage.completion_tokens > 0
    assert result.token_usage.total_tokens == (
        result.token_usage.prompt_tokens + result.token_usage.completion_tokens
    )


def _request(
    *,
    snapshots: Sequence[CampaignSnapshot] | None = None,
    findings: Sequence[AnomalyFinding] | None = None,
    deterministic_report_summary: str = "# deterministic report\n",
) -> LLMInterpretationRequest:
    return LLMInterpretationRequest(
        snapshots=tuple(snapshots if snapshots is not None else [_snapshot()]),
        findings=tuple(findings if findings is not None else []),
        deterministic_report_summary=deterministic_report_summary,
    )


def _snapshot() -> CampaignSnapshot:
    return CampaignSnapshot(
        campaign_id="cmp-search-brand",
        scraped_row=_row(),
        campaign_metadata=_campaign(),
        analytics_metrics=_analytics(),
        aggregated_at=REFERENCE_TIME,
    )


def _snapshot_missing_analytics() -> CampaignSnapshot:
    return CampaignSnapshot(
        campaign_id="cmp-search-brand",
        scraped_row=_row(),
        campaign_metadata=_campaign(),
        analytics_metrics=None,
        data_quality_flags=(DataQualityFlag.MISSING_ANALYTICS_METRICS,),
        data_quality_notes=("Analytics GraphQL metrics are unavailable.",),
        requires_human_review=True,
        aggregated_at=REFERENCE_TIME,
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


def _finding(
    *,
    message: str = "Campaign ROI is below the configured minimum threshold.",
    source_evidence: Mapping[str, object] | None = None,
) -> AnomalyFinding:
    return AnomalyFinding(
        campaign_id="cmp-search-brand",
        anomaly_type=AnomalyType.NEGATIVE_ROI,
        severity=AnomalySeverity.CRITICAL,
        message=message,
        source="deterministic_anomaly_detector",
        source_evidence=dict(source_evidence or {"roi": -0.2}),
        requires_human_review=True,
    )
