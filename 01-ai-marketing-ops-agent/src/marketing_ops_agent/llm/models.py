"""Typed models for optional LLM business interpretation."""

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator

from marketing_ops_agent.aggregation import CampaignSnapshot
from marketing_ops_agent.anomaly import AnomalyFinding
from marketing_ops_agent.observability import WorkflowRunRecord


class LLMInterpretationStatus(StrEnum):
    """Lifecycle state for an optional LLM interpretation attempt."""

    DISABLED = "disabled"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class LLMActionPriority(StrEnum):
    """Business priority for an LLM-suggested follow-up."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class LLMTokenUsage(BaseModel):
    """Token accounting returned by an LLM provider when available."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    prompt_tokens: int = Field(ge=0)
    completion_tokens: int = Field(ge=0)
    total_tokens: int = Field(ge=0)


class LLMRecommendedAction(BaseModel):
    """Structured recommendation proposed from deterministic findings."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    title: str = Field(min_length=1)
    rationale: str = Field(min_length=1)
    priority: LLMActionPriority = LLMActionPriority.MEDIUM
    campaign_id: str | None = None
    source_anomaly_types: tuple[str, ...] = ()
    requires_human_approval: bool = False

    @field_validator("title", "rationale", "campaign_id")
    @classmethod
    def strip_optional_text(cls, value: str | None) -> str | None:
        """Trim optional recommendation text fields and reject blanks.

        Args:
            value: Raw text value.

        Returns:
            Stripped text or `None`.

        Raises:
            ValueError: If a provided value is blank after trimming.
        """
        if value is None:
            return None
        stripped = value.strip()
        if not stripped:
            raise ValueError("text values must not be blank")
        return stripped

    @field_validator("source_anomaly_types")
    @classmethod
    def strip_source_anomaly_types(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        """Trim source anomaly type labels and reject blank entries.

        Args:
            value: Raw anomaly type labels.

        Returns:
            Stripped anomaly type labels.

        Raises:
            ValueError: If any label is blank after trimming.
        """
        stripped_values = tuple(item.strip() for item in value)
        if any(not item for item in stripped_values):
            raise ValueError("source_anomaly_types must not contain blank values")
        return stripped_values


class LLMInterpretationRequest(BaseModel):
    """Validated input package for downstream LLM interpretation."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    snapshots: tuple[CampaignSnapshot, ...] = ()
    findings: tuple[AnomalyFinding, ...] = ()
    deterministic_report_summary: str = ""
    workflow_run: WorkflowRunRecord | None = None


class LLMInterpretationResult(BaseModel):
    """Structured business interpretation returned by the optional LLM layer."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    status: LLMInterpretationStatus
    provider: str = Field(min_length=1)
    model: str = Field(min_length=1)
    generated_at: datetime
    summary: str = ""
    facts: tuple[str, ...] = ()
    recommendations: tuple[LLMRecommendedAction, ...] = ()
    data_quality_warnings: tuple[str, ...] = ()
    source_campaign_count: int = Field(ge=0)
    source_finding_count: int = Field(ge=0)
    token_usage: LLMTokenUsage | None = None
    error_message: str | None = None

    @field_validator("generated_at")
    @classmethod
    def normalize_generated_at(cls, value: datetime) -> datetime:
        """Normalize interpretation timestamps to UTC.

        Args:
            value: Timezone-aware generation timestamp.

        Returns:
            UTC-normalized timestamp.

        Raises:
            ValueError: If the timestamp is naive.
        """
        if value.tzinfo is None:
            raise ValueError("generated_at must be timezone-aware")
        return value.astimezone(UTC)

    @field_validator("summary", "provider", "model", "error_message")
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        """Trim scalar text fields while preserving optional null values.

        Args:
            value: Raw text value.

        Returns:
            Stripped text, empty string or `None`.
        """
        if value is None:
            return None
        stripped = value.strip()
        if not stripped and value:
            return ""
        return stripped

    @field_validator("facts", "data_quality_warnings")
    @classmethod
    def strip_text_tuple(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        """Trim interpretation text tuples and reject blank entries.

        Args:
            value: Raw text tuple.

        Returns:
            Stripped text tuple.

        Raises:
            ValueError: If any entry is blank after trimming.
        """
        stripped_values = tuple(item.strip() for item in value)
        if any(not item for item in stripped_values):
            raise ValueError("text tuples must not contain blank values")
        return stripped_values
