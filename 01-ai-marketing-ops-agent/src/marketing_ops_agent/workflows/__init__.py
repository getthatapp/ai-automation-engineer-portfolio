"""Deterministic workflow orchestration package."""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from marketing_ops_agent.workflows.daily_marketing_report import (
        DailyMarketingReportWorkflow,
        WorkflowExecutionError,
        build_task_requests,
        run_daily_marketing_report_workflow,
    )
    from marketing_ops_agent.workflows.models import DailyMarketingReportResult

__all__ = [
    "DailyMarketingReportResult",
    "DailyMarketingReportWorkflow",
    "WorkflowExecutionError",
    "build_task_requests",
    "run_daily_marketing_report_workflow",
]


def __getattr__(name: str) -> Any:
    """Lazily expose workflow APIs without importing executable modules eagerly."""

    if name == "DailyMarketingReportResult":
        from marketing_ops_agent.workflows.models import DailyMarketingReportResult

        return DailyMarketingReportResult

    if name in {
        "DailyMarketingReportWorkflow",
        "WorkflowExecutionError",
        "build_task_requests",
        "run_daily_marketing_report_workflow",
    }:
        from marketing_ops_agent.workflows import daily_marketing_report

        return getattr(daily_marketing_report, name)

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
