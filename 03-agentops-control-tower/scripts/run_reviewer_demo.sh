#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${PROJECT_ROOT}"

# shellcheck source=scripts/demo_dataset.sh
source "${PROJECT_ROOT}/scripts/demo_dataset.sh"

echo "Running reviewer-friendly AgentOps Control Tower demo..."

demo_dir="${PROJECT_ROOT}/exports/reviewer-demo"
input_dir="${demo_dir}/input"
exports_dir="${demo_dir}"

rm -rf "${demo_dir}"
mkdir -p "${input_dir}" "${exports_dir}"

create_agentops_demo_dataset "${input_dir}"

summary_json="${exports_dir}/summary.json"
timeline_json="${exports_dir}/timeline.json"
markdown_report="${exports_dir}/agentops-report.md"
html_report="${exports_dir}/agentops-report.html"

source_args=(
  "--run-history" "${AGENTOPS_DEMO_RUN_HISTORY}"
  "--approval-requests" "${AGENTOPS_DEMO_APPROVALS}"
  "--report" "${AGENTOPS_DEMO_REPORT_REVIEW}"
  "--tool-evidence" "${AGENTOPS_DEMO_TOOL_NOT_READY}"
  "--guardrail-output" "${AGENTOPS_DEMO_GUARDRAIL_BLOCKED}"
)

uv run agentops-control-tower summary "${source_args[@]}" --pretty > "${summary_json}"
uv run agentops-control-tower timeline "${source_args[@]}" --pretty > "${timeline_json}"
uv run agentops-control-tower export-report \
  "${source_args[@]}" \
  --output "${markdown_report}" \
  --overwrite
uv run agentops-control-tower export-report \
  --format html \
  "${source_args[@]}" \
  --output "${html_report}" \
  --overwrite

uv run python - "${summary_json}" "${timeline_json}" <<'PY'
import json
import sys
from pathlib import Path

summary = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
timeline = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))

print()
print("Reviewer demo summary:")
print(f"- overall_status={summary['overall_status']}")
print(f"- workflow_runs={summary['workflow_runs']['total']}")
print(f"- workflow_failed={summary['workflow_runs']['failed_count']}")
print(
    "- workflow_human_review_required="
    f"{summary['workflow_runs']['human_review_required_count']}"
)
print(f"- approvals={summary['approvals']['total']}")
print(f"- approvals_pending={summary['approvals']['pending_count']}")
print(f"- tools_not_ready={summary['tools']['not_ready_count']}")
print(f"- guardrails_failed_or_blocked={summary['guardrails']['failed_or_blocked_count']}")
print(f"- timeline_events={len(timeline['events'])}")
print("- recommended_actions:")
for action in summary["recommended_actions"]:
    print(f"  - {action}")
PY

echo
echo "Generated reviewer artifacts:"
echo "- output_dir=${demo_dir}"
echo "- summary_json=${summary_json}"
echo "- timeline_json=${timeline_json}"
echo "- markdown_report=${markdown_report}"
echo "- html_report=${html_report}"
echo "- html_heading=$(grep -m 1 '<h1>' "${html_report}" | sed 's/^[[:space:]]*//')"
echo "- html_size_bytes=$(wc -c < "${html_report}" | tr -d ' ')"
echo "- open_command=open exports/reviewer-demo/agentops-report.html"
echo
echo "Dataset notes:"
echo "- workflow runs: succeeded, needs_approval, failed"
echo "- approvals: pending, approved, rejected"
echo "- main report: $(basename "${AGENTOPS_DEMO_REPORT_REVIEW}")"
echo "- comparison report generated but not ingested: $(basename "${AGENTOPS_DEMO_REPORT_HEALTHY}")"
echo "- tool evidence used: $(basename "${AGENTOPS_DEMO_TOOL_NOT_READY}")"
echo "- guardrail output used: $(basename "${AGENTOPS_DEMO_GUARDRAIL_BLOCKED}")"
echo
echo "Open the HTML report with:"
echo "open exports/reviewer-demo/agentops-report.html"
