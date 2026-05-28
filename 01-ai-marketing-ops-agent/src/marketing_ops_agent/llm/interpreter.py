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
        self._provider = provider or DeterministicMockLLMProvider()
        self._enabled = enabled
        self._prompt_builder = prompt_builder
        self._clock = clock or (lambda: datetime.now(UTC))

    async def interpret(
        self,
        request: LLMInterpretationRequest,
    ) -> LLMInterpretationResult:
        """Return structured interpretation, or a safe non-raising failure result."""

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
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)
