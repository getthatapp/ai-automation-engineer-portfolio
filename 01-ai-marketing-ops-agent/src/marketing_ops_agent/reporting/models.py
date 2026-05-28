"""Typed models for deterministic Markdown report generation."""

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ReportMetadata(BaseModel):
    """Metadata attached to a generated marketing operations report."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    title: str = Field(default="Daily Marketing Operations Report", min_length=1)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("title")
    @classmethod
    def strip_title(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("title must not be blank")
        return stripped
