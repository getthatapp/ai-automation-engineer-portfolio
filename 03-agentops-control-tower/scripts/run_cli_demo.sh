#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${PROJECT_ROOT}"

# shellcheck source=scripts/demo_dataset.sh
source "${PROJECT_ROOT}/scripts/demo_dataset.sh"

echo "Running local AgentOps CLI demo with richer temporary sample files..."

temp_dir="$(mktemp -d "${TMPDIR:-/tmp}/agentops-control-tower-cli-demo.XXXXXX")"
trap 'rm -rf "${temp_dir}"' EXIT

create_agentops_demo_dataset "${temp_dir}"

exported_report="${temp_dir}/exports/agentops-report.md"

source_args=(
  "--run-history" "${AGENTOPS_DEMO_RUN_HISTORY}"
  "--approval-requests" "${AGENTOPS_DEMO_APPROVALS}"
  "--report" "${AGENTOPS_DEMO_REPORT_REVIEW}"
  "--tool-evidence" "${AGENTOPS_DEMO_TOOL_NOT_READY}"
  "--guardrail-output" "${AGENTOPS_DEMO_GUARDRAIL_BLOCKED}"
)

echo "workflow_records=3"
echo "approval_records=3"
echo "generated_reports=2"
echo "main_report=$(basename "${AGENTOPS_DEMO_REPORT_REVIEW}")"
echo "comparison_report=$(basename "${AGENTOPS_DEMO_REPORT_HEALTHY}")"
echo "note=CLI accepts one Markdown report path per command; this demo uses the review-focused report."

echo
echo "Summary JSON:"
uv run agentops-control-tower summary "${source_args[@]}" --pretty

echo
echo "Timeline JSON:"
uv run agentops-control-tower timeline "${source_args[@]}" --pretty

echo
echo "Exporting Markdown report:"
uv run agentops-control-tower export-report "${source_args[@]}" --output "${exported_report}"
echo "report_path=${exported_report}"
echo "report_heading=$(sed -n '1p' "${exported_report}")"
