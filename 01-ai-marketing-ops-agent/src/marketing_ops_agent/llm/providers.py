"""Provider abstraction and deterministic provider for LLM interpretation."""

from datetime import UTC, datetime
from typing import Protocol

from marketing_ops_agent.anomaly import AnomalyFinding, AnomalySeverity
from marketing_ops_agent.llm.models import (
    LLMActionPriority,
    LLMInterpretationRequest,
    LLMInterpretationResult,
    LLMInterpretationStatus,
    LLMRecommendedAction,
    LLMTokenUsage,
)


class LLMInterpretationProvider(Protocol):
    """Provider contract for future real LLM implementations."""

    @property
    def provider_name(self) -> str:
        """Human-readable provider name."""

    @property
    def model_name(self) -> str:
        """Human-readable model name."""

    async def interpret(
        self,
        *,
        request: LLMInterpretationRequest,
        prompt: str,
    ) -> LLMInterpretationResult:
        """Return structured interpretation for a prepared prompt."""


class DeterministicMockLLMProvider:
    """Deterministic provider used in tests and local no-key environments."""

    def __init__(
        self,
        *,
        provider_name: str = "mock",
        model_name: str = "deterministic-marketing-interpreter",
        include_token_usage: bool = True,
    ) -> None:
        self._provider_name = provider_name
        self._model_name = model_name
        self._include_token_usage = include_token_usage

    @property
    def provider_name(self) -> str:
        return self._provider_name

    @property
    def model_name(self) -> str:
        return self._model_name

    async def interpret(
        self,
        *,
        request: LLMInterpretationRequest,
        prompt: str,
    ) -> LLMInterpretationResult:
        """Return deterministic structured output without external API calls."""

        findings = tuple(request.findings)
        snapshots = tuple(request.snapshots)
        critical_count = sum(
            1 for finding in findings if finding.severity is AnomalySeverity.CRITICAL
        )
        warning_count = sum(
            1 for finding in findings if finding.severity is AnomalySeverity.WARNING
        )
        review_count = sum(
            1
            for snapshot in snapshots
            if snapshot.requires_human_review
        ) + sum(1 for finding in findings if finding.requires_human_review)
        data_quality_warnings = tuple(
            (
                f"{snapshot.campaign_id}: "
                f"{', '.join(flag.value for flag in snapshot.data_quality_flags)}"
            )
            for snapshot in snapshots
            if snapshot.data_quality_flags
        )

        return LLMInterpretationResult(
            status=LLMInterpretationStatus.SUCCEEDED,
            provider=self.provider_name,
            model=self.model_name,
            generated_at=datetime.now(UTC),
            summary=(
                f"Processed {len(snapshots)} validated campaign snapshots with "
                f"{len(findings)} deterministic findings."
            ),
            facts=(
                f"Critical deterministic findings: {critical_count}.",
                f"Warning deterministic findings: {warning_count}.",
                f"Human-review signals: {review_count}.",
            ),
            recommendations=tuple(
                _action_from_finding(finding)
                for finding in findings
                if finding.severity is AnomalySeverity.CRITICAL
                or finding.requires_human_review
            ),
            data_quality_warnings=data_quality_warnings,
            source_campaign_count=len(snapshots),
            source_finding_count=len(findings),
            token_usage=(
                _estimate_token_usage(prompt)
                if self._include_token_usage
                else None
            ),
        )


def _action_from_finding(finding: AnomalyFinding) -> LLMRecommendedAction:
    return LLMRecommendedAction(
        title=f"Review {finding.anomaly_type.value} for {finding.campaign_id}",
        rationale=(
            "Recommendation is based on deterministic finding: "
            f"{finding.message}"
        ),
        priority=(
            LLMActionPriority.HIGH
            if finding.severity is AnomalySeverity.CRITICAL
            else LLMActionPriority.MEDIUM
        ),
        campaign_id=finding.campaign_id,
        source_anomaly_types=(finding.anomaly_type.value,),
        requires_human_approval=finding.requires_human_review,
    )


def _estimate_token_usage(prompt: str) -> LLMTokenUsage:
    prompt_tokens = max(len(prompt.split()), 1)
    completion_tokens = 80
    return LLMTokenUsage(
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=prompt_tokens + completion_tokens,
    )
