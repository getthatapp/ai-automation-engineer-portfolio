"""Typed input and output models for deterministic local tools."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

try:
    from pydantic import BaseModel, ConfigDict, Field, ValidationError
except ImportError:
    _MISSING = object()

    class ValidationError(ValueError):  # type: ignore[no-redef]
        """Minimal validation error used when Pydantic is unavailable."""

        def __init__(self, errors: list[dict[str, Any]]) -> None:
            """Initialize the fallback validation error.

            Args:
                errors: Structured validation errors.
            """
            super().__init__("Validation failed")
            self._errors = errors

        def errors(self) -> list[dict[str, Any]]:
            """Return structured validation errors.

            Returns:
                Validation errors matching the Pydantic `errors()` shape used here.
            """
            return self._errors

    class _FieldInfo:
        """Fallback field metadata for default values and numeric bounds."""

        def __init__(
            self,
            default: Any = _MISSING,
            *,
            default_factory: Callable[[], Any] | None = None,
            ge: int | None = None,
            le: int | None = None,
        ) -> None:
            """Initialize fallback field metadata.

            Args:
                default: Optional field default.
                default_factory: Optional callable used to build a default value.
                ge: Optional inclusive minimum numeric value.
                le: Optional inclusive maximum numeric value.
            """
            self.default = default
            self.default_factory = default_factory
            self.ge = ge
            self.le = le

    def Field(  # type: ignore[no-redef]
        default: Any = _MISSING,
        *,
        default_factory: Callable[[], Any] | None = None,
        ge: int | None = None,
        le: int | None = None,
    ) -> Any:
        """Create fallback field metadata when Pydantic is unavailable.

        Args:
            default: Optional field default.
            default_factory: Optional callable used to build a default value.
            ge: Optional inclusive minimum numeric value.
            le: Optional inclusive maximum numeric value.

        Returns:
            Fallback field metadata.
        """
        return _FieldInfo(default, default_factory=default_factory, ge=ge, le=le)

    def ConfigDict(**kwargs: Any) -> dict[str, Any]:  # type: ignore[no-redef]  # noqa: N802
        """Create fallback model configuration.

        Args:
            **kwargs: Configuration values.

        Returns:
            The provided configuration values.
        """
        return kwargs

    class BaseModel:  # type: ignore[no-redef]
        """Small fallback model used only when Pydantic is unavailable."""

        def __init__(self, **data: Any) -> None:
            """Initialize the fallback model from keyword values.

            Args:
                **data: Field values for the model.

            Raises:
                ValidationError: If a required field is missing or a bound fails.
            """
            errors: list[dict[str, Any]] = []
            for field_name in self._field_names():
                field_info = getattr(self.__class__, field_name, _MISSING)
                if field_name in data:
                    value = data[field_name]
                else:
                    value = self._default_for_field(field_name, field_info, errors)
                    if errors and errors[-1]["loc"] == (field_name,):
                        continue
                self._validate_field(field_name, value, field_info, errors)
                setattr(self, field_name, value)
            if errors:
                raise ValidationError(errors)

        @classmethod
        def _field_names(cls) -> list[str]:
            """Return annotated field names for a fallback model class.

            Returns:
                Ordered annotated field names from base classes and the concrete class.
            """
            field_names: list[str] = []
            for model_class in reversed(cls.__mro__):
                for field_name in getattr(model_class, "__annotations__", {}):
                    if field_name != "model_config" and field_name not in field_names:
                        field_names.append(field_name)
            return field_names

        def _default_for_field(
            self,
            field_name: str,
            field_info: Any,
            errors: list[dict[str, Any]],
        ) -> Any:
            """Resolve a default value for a fallback model field.

            Args:
                field_name: Name of the field being resolved.
                field_info: Class-level field metadata or default value.
                errors: Mutable validation error list.

            Returns:
                Field default value when available.
            """
            if isinstance(field_info, _FieldInfo):
                if field_info.default_factory is not None:
                    return field_info.default_factory()
                if field_info.default is not _MISSING:
                    return field_info.default
            elif field_info is not _MISSING:
                return field_info
            errors.append({"loc": (field_name,), "msg": "Field required"})
            return None

        def _validate_field(
            self,
            field_name: str,
            value: Any,
            field_info: Any,
            errors: list[dict[str, Any]],
        ) -> None:
            """Validate fallback field bounds.

            Args:
                field_name: Name of the field being validated.
                value: Field value.
                field_info: Class-level field metadata or default value.
                errors: Mutable validation error list.
            """
            if not isinstance(field_info, _FieldInfo):
                return
            if field_info.ge is not None and value < field_info.ge:
                errors.append(
                    {
                        "loc": (field_name,),
                        "msg": f"Input should be greater than or equal to {field_info.ge}",
                    }
                )
            if field_info.le is not None and value > field_info.le:
                errors.append(
                    {
                        "loc": (field_name,),
                        "msg": f"Input should be less than or equal to {field_info.le}",
                    }
                )

        def model_dump(self) -> dict[str, Any]:
            """Return a serializable dictionary of model fields.

            Returns:
                Field names and values for this model.
            """
            return {field_name: getattr(self, field_name) for field_name in self._field_names()}

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


class ReportSummary(ToolModel):
    """Summary values explicitly extracted from a deterministic Markdown report."""

    generated_timestamp: str | None = None
    campaigns_processed: int | None = None
    critical_findings: int | None = None
    warning_findings: int | None = None
    campaigns_requiring_human_review: int | None = None


class ValidateReportResult(ToolModel):
    """Output schema for Markdown report section validation."""

    valid: bool
    report_path: str
    file_exists: bool
    required_sections: list[str]
    found_sections: list[str]
    missing_sections: list[str]
    summary: ReportSummary = Field(default_factory=ReportSummary)
    warnings: list[str] = Field(default_factory=list)
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
    total_records_read: int = 0
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
    total_records_read: int = 0
    pending_count: int = 0
    malformed_lines: list[JsonLineError]
    errors: list[str] = Field(default_factory=list)


class CheckRuntimeCleanInput(ToolModel):
    """Input schema for checking Project 1 runtime artifact cleanliness."""

    project_path: Path


class RuntimeArtifactCounts(ToolModel):
    """Counts of generated Project 1 runtime artifacts by type."""

    reports: int = 0
    run_history: int = 0
    approval_requests: int = 0
    pycache: int = 0
    pyc: int = 0


class CheckRuntimeCleanResult(ToolModel):
    """Output schema for runtime artifact cleanliness checks."""

    clean: bool
    project_path: str
    found_paths: list[str]
    artifact_counts: RuntimeArtifactCounts = Field(default_factory=RuntimeArtifactCounts)
    checked_patterns: list[str]
    errors: list[str] = Field(default_factory=list)


class GenerateDemoBriefInput(ToolModel):
    """Input schema for generating a deterministic Project 1 demo brief."""

    project_path: Path


class ReadinessCheck(ToolModel):
    """A named deterministic Project 1 readiness check."""

    name: str
    ready: bool
    present_paths: list[str] = Field(default_factory=list)
    missing_paths: list[str] = Field(default_factory=list)


class GenerateDemoBriefResult(ToolModel):
    """Output schema for deterministic Project 1 demo readiness summaries."""

    project_path: str
    ready: bool
    brief: str
    present_paths: list[str]
    missing_paths: list[str]
    readiness_checklist: list[ReadinessCheck] = Field(default_factory=list)
    local_commands: list[str]
    errors: list[str] = Field(default_factory=list)


class ToolDefinition(ToolModel):
    """Describes a locally registered deterministic tool."""

    name: str
    description: str


__all__ = [
    "CheckRuntimeCleanInput",
    "CheckRuntimeCleanResult",
    "GenerateDemoBriefInput",
    "GenerateDemoBriefResult",
    "JsonLineError",
    "ListPendingApprovalsInput",
    "ListPendingApprovalsResult",
    "PendingApprovalSummary",
    "ReadRunHistoryInput",
    "ReadRunHistoryResult",
    "ReadinessCheck",
    "ReportSummary",
    "RuntimeArtifactCounts",
    "ToolDefinition",
    "ToolModel",
    "ValidateReportInput",
    "ValidateReportResult",
    "ValidationError",
]
