"""Core Pydantic models for the marketing operations workflow."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class Channel(StrEnum):
    """Supported marketing channels for the initial workflow."""

    SEARCH = "search"
    SOCIAL = "social"
    EMAIL = "email"
    DISPLAY = "display"


class WorkflowStatus(StrEnum):
    """Lifecycle status for a workflow run."""

    PENDING = "pending"
    RUNNING = "running"
    NEEDS_APPROVAL = "needs_approval"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class RecommendationImpact(StrEnum):
    """Business impact level for report recommendations."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class CampaignMetrics(BaseModel):
    """Validated numeric metrics for a campaign snapshot."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    impressions: int = Field(ge=0)
    clicks: int = Field(ge=0)
    conversions: int = Field(ge=0)
    spend: float = Field(ge=0)
    revenue: float = Field(ge=0)

    @property
    def ctr(self) -> float:
        """Click-through rate."""

        if self.impressions == 0:
            return 0.0
        return self.clicks / self.impressions

    @property
    def conversion_rate(self) -> float:
        """Conversion rate from clicks to conversions."""

        if self.clicks == 0:
            return 0.0
        return self.conversions / self.clicks

    @property
    def return_on_ad_spend(self) -> float:
        """Revenue divided by spend."""

        if self.spend == 0:
            return 0.0
        return self.revenue / self.spend


class Campaign(BaseModel):
    """Marketing campaign data normalized from source systems."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    campaign_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    channel: Channel
    source_url: HttpUrl | None = None
    metrics: CampaignMetrics
    collected_at: datetime

    @field_validator("campaign_id", "name")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("value must not be blank")
        return stripped


class ReportRecommendation(BaseModel):
    """A recommendation intended for the generated marketing report."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    title: str = Field(min_length=1)
    rationale: str = Field(min_length=1)
    impact: RecommendationImpact
    requires_human_approval: bool = False

    @field_validator("title", "rationale")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("value must not be blank")
        return stripped


class WorkflowRunLog(BaseModel):
    """Minimal auditable record for a workflow execution."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    run_id: str = Field(min_length=1)
    status: WorkflowStatus
    started_at: datetime
    finished_at: datetime | None = None
    campaigns_processed: int = Field(default=0, ge=0)
    retry_count: int = Field(default=0, ge=0)
    error_message: str | None = None

    @field_validator("run_id")
    @classmethod
    def strip_run_id(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("run_id must not be blank")
        return stripped
