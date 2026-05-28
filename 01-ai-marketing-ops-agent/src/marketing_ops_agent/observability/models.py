"""Typed models for persisted workflow run observability."""

import re
from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, field_validator

from marketing_ops_agent.models import WorkflowStatus

_KEYED_SECRET_PATTERN = re.compile(
    r"(?i)\b(password|passwd|pwd|token|secret|api[_-]?key|authorization)"
    r"(\s*[=:]\s*)"
    r"([^,\s;]+)"
)
_AUTHORIZATION_BEARER_PATTERN = re.compile(
    r"(?i)\b(authorization)(\s*[=:]\s*)bearer\s+[A-Za-z0-9._~+/=-]+"
)
_BEARER_SECRET_PATTERN = re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]+")


class WorkflowRunRecord(BaseModel):
    """Durable summary of one deterministic workflow execution."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    run_id: str = Field(min_length=1)
    workflow_name: str = Field(min_length=1)
    status: WorkflowStatus
    started_at: datetime
    finished_at: datetime
    duration_seconds: float = Field(ge=0)
    report_path: Path | None = None
    snapshot_count: int = Field(ge=0)
    finding_count: int = Field(ge=0)
    critical_finding_count: int = Field(ge=0)
    human_review_required: bool
    created_task_ids: tuple[str, ...] = ()
    task_error_count: int = Field(ge=0)
    data_quality_summary: dict[str, int] = Field(default_factory=dict)
    failure_type: str | None = None
    failure_message: str | None = None

    @field_validator("run_id", "workflow_name")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("value must not be blank")
        return stripped

    @field_validator("created_task_ids")
    @classmethod
    def strip_task_ids(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        stripped_values = tuple(task_id.strip() for task_id in value)
        if any(not task_id for task_id in stripped_values):
            raise ValueError("created_task_ids must not contain blank values")
        return stripped_values

    @field_validator("started_at", "finished_at")
    @classmethod
    def normalize_datetime(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("workflow run timestamps must be timezone-aware")
        return value.astimezone(UTC)

    @field_validator("failure_type", "failure_message")
    @classmethod
    def sanitize_failure_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        if not stripped:
            return None
        return sanitize_observability_text(stripped)

    @field_validator("data_quality_summary")
    @classmethod
    def validate_quality_summary(cls, value: dict[str, int]) -> dict[str, int]:
        return {
            key.strip(): count
            for key, count in sorted(value.items())
            if key.strip() and count > 0
        }


def sanitize_observability_text(value: str) -> str:
    """Redact common inline credential shapes before persisting failure text."""

    redacted = _AUTHORIZATION_BEARER_PATTERN.sub(r"\1\2Bearer [REDACTED]", value)
    redacted = _KEYED_SECRET_PATTERN.sub(r"\1\2[REDACTED]", redacted)
    return _BEARER_SECRET_PATTERN.sub("Bearer [REDACTED]", redacted)
