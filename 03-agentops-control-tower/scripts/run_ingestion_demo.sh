#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${PROJECT_ROOT}"

echo "Running local AgentOps ingestion demo with temporary sample files..."

uv run python - <<'PY'
import json
import tempfile
from pathlib import Path

from agentops_control_tower import ingest_local_agentops_sources

with tempfile.TemporaryDirectory(prefix="agentops-control-tower-demo-") as temp_dir:
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

    result = ingest_local_agentops_sources(
        run_history_path=run_history,
        approval_requests_path=approvals,
        markdown_report_path=report,
        guardrail_output_text_path=guardrail,
    )

    print(f"records={result.record_count}")
    print(f"warnings={len(result.warnings)}")
    print(f"errors={len(result.errors)}")
    print(f"ok={str(result.ok).lower()}")
PY
