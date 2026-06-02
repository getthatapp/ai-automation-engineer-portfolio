"""Typed input and output models for deterministic local tools."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ToolModel(BaseModel):
    """Base Pydantic model for tool input and output schemas."""

    model_config = ConfigDict(arbitrary_types_allowed=True)


class JsonLineError(ToolModel):
    """Describes a malformed JSONL line found while reading a local artifact."""

    line_number: int = Field(ge=1)
    message: str


class ValidateReportInput(ToolModel):
    """Input schema for validating a deterministic Markdown report."""

    report_path: Path


class ValidateReportResult(ToolModel):
    """Output schema for Markdown report section validation."""

    valid: bool
    report_path: str
    file_exists: bool
    required_sections: list[str]
    found_sections: list[str]
    missing_sections: list[str]
    errors: list[str] = Field(default_factory=list)


class ReadRunHistoryInput(ToolModel):
    """Input schema for reading Project 1 workflow run history JSONL."""

    jsonl_path: Path
    limit: int = Field(default=5, ge=1, le=100)


class ReadRunHistoryResult(ToolModel):
    """Output schema for recent workflow run history records."""

    jsonl_path: str
    file_exists: bool
    records: list[dict[str, Any]]
    malformed_lines: list[JsonLineError]
    errors: list[str] = Field(default_factory=list)


class ListPendingApprovalsInput(ToolModel):
    """Input schema for listing pending approval records from JSONL."""

    jsonl_path: Path


class PendingApprovalSummary(ToolModel):
    """Summary of a pending approval request safe for agent display."""

    approval_id: str | None = None
    run_id: str | None = None
    campaign_id: str | None = None
    source: str | None = None
    source_reference: str | None = None
    risk_level: str | None = None
    status: str | None = None
    title: str | None = None
    created_at: str | None = None


class ListPendingApprovalsResult(ToolModel):
    """Output schema for pending approval summaries."""

    jsonl_path: str
    file_exists: bool
    pending_approvals: list[PendingApprovalSummary]
    malformed_lines: list[JsonLineError]
    errors: list[str] = Field(default_factory=list)


class CheckRuntimeCleanInput(ToolModel):
    """Input schema for checking Project 1 runtime artifact cleanliness."""

    project_path: Path


class CheckRuntimeCleanResult(ToolModel):
    """Output schema for runtime artifact cleanliness checks."""

    clean: bool
    project_path: str
    found_paths: list[str]
    checked_patterns: list[str]
    errors: list[str] = Field(default_factory=list)


class GenerateDemoBriefInput(ToolModel):
    """Input schema for generating a deterministic Project 1 demo brief."""

    project_path: Path


class GenerateDemoBriefResult(ToolModel):
    """Output schema for deterministic Project 1 demo readiness summaries."""

    project_path: str
    ready: bool
    brief: str
    present_paths: list[str]
    missing_paths: list[str]
    local_commands: list[str]
    errors: list[str] = Field(default_factory=list)


class ToolDefinition(ToolModel):
    """Describes a locally registered deterministic tool."""

    name: str
    description: str
