"""Typed models for deterministic human approval workflows."""

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from marketing_ops_agent.observability import sanitize_observability_text


class ApprovalStatus(StrEnum):
    """Lifecycle status for a human approval request."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class ApprovalRiskLevel(StrEnum):
    """Business risk level for approval-gated automation."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ApprovalSource(StrEnum):
    """Source system that created an approval request."""

    DETERMINISTIC_FINDING = "deterministic_finding"
    LLM_RECOMMENDATION = "llm_recommendation"


ApprovalEvidenceValue = str | int | float | bool | None


class ApprovalDecision(BaseModel):
    """Human decision recorded for an approval request."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    status: ApprovalStatus
    decided_at: datetime
    decided_by: str = Field(min_length=1)
    reason: str = Field(default="", max_length=2_000)

    @model_validator(mode="after")
    def require_terminal_status(self) -> "ApprovalDecision":
        """Require approval decisions to be approve or reject states.

        Returns:
            Validated approval decision.

        Raises:
            ValueError: If the decision status is not approved or rejected.
        """

        if self.status not in {ApprovalStatus.APPROVED, ApprovalStatus.REJECTED}:
            raise ValueError("approval decision status must be approved or rejected")
        return self

    @field_validator("decided_at")
    @classmethod
    def normalize_decided_at(cls, value: datetime) -> datetime:
        """Normalize decision timestamps to UTC.

        Args:
            value: Timezone-aware decision timestamp.

        Returns:
            UTC-normalized timestamp.

        Raises:
            ValueError: If the timestamp is naive.
        """

        if value.tzinfo is None:
            raise ValueError("decided_at must be timezone-aware")
        return value.astimezone(UTC)

    @field_validator("decided_by", "reason")
    @classmethod
    def sanitize_text(cls, value: str) -> str:
        """Trim and redact decision text before persistence.

        Args:
            value: Raw decision text.

        Returns:
            Sanitized text.
        """

        return sanitize_observability_text(value.strip())


class ApprovalRequest(BaseModel):
    """Approval-gated action request persisted for human review."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    approval_id: str = Field(min_length=1)
    run_id: str | None = None
    campaign_id: str | None = None
    source: ApprovalSource
    source_reference: str = Field(min_length=1)
    risk_level: ApprovalRiskLevel
    status: ApprovalStatus = ApprovalStatus.PENDING
    title: str = Field(min_length=1, max_length=300)
    rationale: str = Field(min_length=1, max_length=2_000)
    source_evidence: dict[str, ApprovalEvidenceValue] = Field(default_factory=dict)
    created_at: datetime
    decision: ApprovalDecision | None = None

    @model_validator(mode="after")
    def validate_status_decision_consistency(self) -> "ApprovalRequest":
        """Require terminal statuses to include matching decisions.

        Returns:
            Validated approval request.

        Raises:
            ValueError: If request status and decision state disagree.
        """

        if self.status is ApprovalStatus.PENDING and self.decision is not None:
            raise ValueError("pending approval requests must not have a decision")
        if self.status in {ApprovalStatus.APPROVED, ApprovalStatus.REJECTED}:
            if self.decision is None:
                raise ValueError("terminal approval requests must include a decision")
            if self.status is not self.decision.status:
                raise ValueError("approval request status must match decision status")
        return self

    @field_validator("created_at")
    @classmethod
    def normalize_created_at(cls, value: datetime) -> datetime:
        """Normalize creation timestamps to UTC.

        Args:
            value: Timezone-aware creation timestamp.

        Returns:
            UTC-normalized timestamp.

        Raises:
            ValueError: If the timestamp is naive.
        """

        if value.tzinfo is None:
            raise ValueError("created_at must be timezone-aware")
        return value.astimezone(UTC)

    @field_validator(
        "approval_id",
        "run_id",
        "campaign_id",
        "source_reference",
        "title",
        "rationale",
    )
    @classmethod
    def sanitize_optional_text(cls, value: str | None) -> str | None:
        """Trim and redact approval text fields before persistence.

        Args:
            value: Optional raw text value.

        Returns:
            Sanitized text or `None`.

        Raises:
            ValueError: If a provided value is blank after trimming.
        """

        if value is None:
            return None
        sanitized = sanitize_observability_text(value.strip())
        if not sanitized:
            raise ValueError("approval text fields must not be blank")
        return sanitized

    @field_validator("source_evidence")
    @classmethod
    def sanitize_source_evidence(
        cls,
        value: dict[str, ApprovalEvidenceValue],
    ) -> dict[str, ApprovalEvidenceValue]:
        """Normalize and redact approval source evidence.

        Args:
            value: Raw source evidence mapping.

        Returns:
            Sorted evidence mapping with blank keys removed and string values
            redacted.
        """

        sanitized: dict[str, ApprovalEvidenceValue] = {}
        for key, item in sorted(value.items()):
            stripped_key = sanitize_observability_text(str(key).strip())
            if not stripped_key:
                continue
            sanitized[stripped_key] = (
                sanitize_observability_text(item.strip())
                if isinstance(item, str)
                else item
            )
        return sanitized
