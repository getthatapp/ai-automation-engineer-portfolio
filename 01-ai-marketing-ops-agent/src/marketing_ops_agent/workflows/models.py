"""Typed models returned by deterministic workflow orchestration."""

from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, field_validator

from marketing_ops_agent.aggregation import CampaignSnapshot
from marketing_ops_agent.anomaly import AnomalyFinding
from marketing_ops_agent.clients import ProjectTask
from marketing_ops_agent.llm import LLMInterpretationResult
from marketing_ops_agent.models import WorkflowStatus
from marketing_ops_agent.notifications import NotificationResult


class DailyMarketingReportResult(BaseModel):
    """Auditable result for one daily marketing report workflow run."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    run_id: str = Field(min_length=1)
    status: WorkflowStatus
    started_at: datetime
    finished_at: datetime
    report_path: Path
    scraped_rows_count: int = Field(ge=0)
    snapshot_count: int = Field(ge=0)
    finding_count: int = Field(ge=0)
    requires_human_review: bool = False
    snapshots: tuple[CampaignSnapshot, ...] = ()
    findings: tuple[AnomalyFinding, ...] = ()
    llm_interpretation: LLMInterpretationResult | None = None
    notification_result: NotificationResult | None = None
    approval_request_ids: tuple[str, ...] = ()
    created_tasks: tuple[ProjectTask, ...] = ()
    task_creation_errors: tuple[str, ...] = ()

    @field_validator("run_id")
    @classmethod
    def strip_run_id(cls, value: str) -> str:
        """Trim workflow run IDs and reject blank values.

        Args:
            value: Raw run ID.

        Returns:
            Stripped non-empty run ID.

        Raises:
            ValueError: If the stripped run ID is blank.
        """
        stripped = value.strip()
        if not stripped:
            raise ValueError("run_id must not be blank")
        return stripped
