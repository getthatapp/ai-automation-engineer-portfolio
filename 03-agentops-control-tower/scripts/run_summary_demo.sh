#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${PROJECT_ROOT}"

echo "Running local AgentOps summary demo with temporary sample files..."

uv run python - <<'PY'
import json
import tempfile
from pathlib import Path

from agentops_control_tower import build_agentops_control_tower_view

with tempfile.TemporaryDirectory(prefix="agentops-control-tower-summary-demo-") as temp_dir:
    root = Path(temp_dir)
    run_history = root / "workflow-runs.jsonl"
    approvals = root / "approval-requests.jsonl"
    report = root / "daily-marketing-report-demo.md"
    guardrail = root / "guardrail.txt"

    run_history.write_text(
        json.dumps(
            {
                "run_id": "daily-marketing-report-demo",
                "workflow_name": "daily_marketing_report",
                "status": "succeeded",
                "started_at": "2026-05-28T12:00:00+00:00",
                "finished_at": "2026-05-28T12:00:03+00:00",
                "duration_seconds": 3.0,
                "snapshot_count": 2,
                "finding_count": 1,
                "critical_finding_count": 0,
                "human_review_required": False,
                "task_error_count": 0,
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    approvals.write_text(
        json.dumps(
            {
                "approval_id": "approval-demo",
                "run_id": "daily-marketing-report-demo",
                "status": "pending",
                "source": "deterministic_finding",
                "source_reference": "cmp-demo:negative_roi",
                "risk_level": "high",
                "title": "Review campaign",
                "rationale": "Demo approval request.",
                "created_at": "2026-05-28T12:00:00+00:00",
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    report.write_text(
        """# Daily Marketing Operations Report

Generated timestamp: 2026-05-28T12:00:00+00:00

## Executive Summary
- Campaigns processed: 2.
- Critical findings: 0.
- Warning findings: 1.
- Campaigns requiring human review: 1.

## Campaign Health Overview
## Critical Anomalies
## Warning Anomalies
## Data Quality Issues
## Human Review Required
## Campaign Snapshot Table
## Deterministic Recommended Actions
## Limitations
""",
        encoding="utf-8",
    )
    guardrail.write_text("guardrail checks passed clean\n", encoding="utf-8")

    view = build_agentops_control_tower_view(
        run_history_path=run_history,
        approval_requests_path=approvals,
        markdown_report_path=report,
        guardrail_output_text_path=guardrail,
    )
    summary = view.summary

    print(f"overall_status={summary.overall_status.value}")
    print(f"workflow_runs={summary.workflow_runs.total}")
    print(f"approvals={summary.approvals.total}")
    print(f"reports={summary.reports.total}")
    print(f"tools={summary.tools.total}")
    print(f"guardrails={summary.guardrails.total}")
    print(f"timeline_events={view.timeline.event_count}")
    print("recommended_actions:")
    for action in summary.recommended_actions:
        print(f"- {action}")
PY
