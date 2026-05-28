"""Optional LLM interpretation service over deterministic workflow outputs."""

import logging
from collections.abc import Callable
from datetime import UTC, datetime

from marketing_ops_agent.llm.errors import LLMInterpretationError
from marketing_ops_agent.llm.models import (
    LLMInterpretationRequest,
    LLMInterpretationResult,
    LLMInterpretationStatus,
)
from marketing_ops_agent.llm.prompts import build_interpretation_prompt
from marketing_ops_agent.llm.providers import (
    DeterministicMockLLMProvider,
    LLMInterpretationProvider,
)
from marketing_ops_agent.observability import sanitize_observability_text

logger = logging.getLogger(__name__)

PromptBuilder = Callable[[LLMInterpretationRequest], str]


class LLMInterpreter:
    """Fail-safe service for optional LLM business interpretation."""

    def __init__(
        self,
        *,
        provider: LLMInterpretationProvider | None = None,
        enabled: bool = True,
        prompt_builder: PromptBuilder = build_interpretation_prompt,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        """Initialize the optional interpreter service.

        Args:
            provider: LLM provider implementation; the deterministic mock is
                used when omitted.
            enabled: Whether interpretation should call the provider.
            prompt_builder: Function that converts validated inputs into a
                provider prompt.
            clock: Optional clock used for disabled or failed results.
        """
        self._provider = provider or DeterministicMockLLMProvider()
        self._enabled = enabled
        self._prompt_builder = prompt_builder
        self._clock = clock or (lambda: datetime.now(UTC))

    async def interpret(
        self,
        request: LLMInterpretationRequest,
    ) -> LLMInterpretationResult:
        """Return structured interpretation, or a safe non-raising failure result.

        Args:
            request: Validated deterministic inputs for interpretation.

        Returns:
            Structured interpretation result. Disabled or unavailable LLM paths
            return `disabled` or `failed` status instead of raising.

        Side Effects:
            May call the configured LLM provider when enabled.
        """

        if not self._enabled:
            return self._status_result(
                request,
                status=LLMInterpretationStatus.DISABLED,
                summary="LLM interpretation is disabled.",
            )

        try:
            prompt = self._prompt_builder(request)
            result = await self._provider.interpret(request=request, prompt=prompt)
        except LLMInterpretationError as exc:
            logger.warning("LLM interpretation failed: %s", exc)
            return self._status_result(
                request,
                status=LLMInterpretationStatus.FAILED,
                error_message=str(exc),
            )
        except Exception as exc:
            logger.exception("Unexpected LLM interpretation failure")
            return self._status_result(
                request,
                status=LLMInterpretationStatus.FAILED,
                error_message=str(exc),
            )

        return result.model_copy(
            update={
                "source_campaign_count": len(request.snapshots),
                "source_finding_count": len(request.findings),
            }
        )

    def _status_result(
        self,
        request: LLMInterpretationRequest,
        *,
        status: LLMInterpretationStatus,
        summary: str = "",
        error_message: str | None = None,
    ) -> LLMInterpretationResult:
        """Build a structured disabled or failed interpretation result.

        Args:
            request: Original interpretation request.
            status: Disabled or failed status to return.
            summary: Optional human-readable status summary.
            error_message: Optional failure text to sanitize.

        Returns:
            Structured result preserving source input counts.
        """
        return LLMInterpretationResult(
            status=status,
            provider=self._provider.provider_name,
            model=self._provider.model_name,
            generated_at=self._normalize_datetime(self._clock()),
            summary=summary,
            source_campaign_count=len(request.snapshots),
            source_finding_count=len(request.findings),
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
