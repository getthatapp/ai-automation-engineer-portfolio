#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${PROJECT_ROOT}"

# shellcheck source=scripts/demo_dataset.sh
source "${PROJECT_ROOT}/scripts/demo_dataset.sh"

echo "Running local AgentOps summary demo with richer temporary sample files..."

temp_dir="$(mktemp -d "${TMPDIR:-/tmp}/agentops-control-tower-summary-demo.XXXXXX")"
trap 'rm -rf "${temp_dir}"' EXIT

create_agentops_demo_dataset "${temp_dir}"

uv run python - \
  "${AGENTOPS_DEMO_RUN_HISTORY}" \
  "${AGENTOPS_DEMO_APPROVALS}" \
  "${AGENTOPS_DEMO_REPORT_REVIEW}" \
  "${AGENTOPS_DEMO_TOOL_NOT_READY}" \
  "${AGENTOPS_DEMO_GUARDRAIL_BLOCKED}" <<'PY'
import sys
from pathlib import Path

from agentops_control_tower import build_agentops_control_tower_view

run_history, approvals, report, tool_evidence, guardrail = map(Path, sys.argv[1:])

view = build_agentops_control_tower_view(
    run_history_path=run_history,
    approval_requests_path=approvals,
    markdown_report_path=report,
    tool_evidence_json_path=tool_evidence,
    guardrail_output_text_path=guardrail,
)
summary = view.summary

print(f"overall_status={summary.overall_status.value}")
print(f"workflow_runs={summary.workflow_runs.total}")
print(f"workflow_failed={summary.workflow_runs.failed_count}")
print(f"workflow_human_review_required={summary.workflow_runs.human_review_required_count}")
print(f"approvals={summary.approvals.total}")
print(f"approvals_pending={summary.approvals.pending_count}")
print(f"reports={summary.reports.total}")
print(f"reports_requiring_human_review={summary.reports.requiring_human_review_count}")
print(f"tools={summary.tools.total}")
print(f"tools_ready={summary.tools.ready_count}")
print(f"tools_not_ready={summary.tools.not_ready_count}")
print(f"guardrails={summary.guardrails.total}")
print(f"guardrails_failed_or_blocked={summary.guardrails.failed_or_blocked_count}")
print(f"timeline_events={view.timeline.event_count}")
print("recommended_actions:")
for action in summary.recommended_actions:
    print(f"- {action}")
PY

echo "comparison_report_available=$(basename "${AGENTOPS_DEMO_REPORT_HEALTHY}")"
echo "note=CLI accepts one Markdown report path per command; richer reviewer demo uses the review-focused report."
