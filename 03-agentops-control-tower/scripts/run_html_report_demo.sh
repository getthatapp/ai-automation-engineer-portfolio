#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${PROJECT_ROOT}"

# shellcheck source=scripts/demo_dataset.sh
source "${PROJECT_ROOT}/scripts/demo_dataset.sh"

echo "Running local AgentOps HTML report demo with richer temporary sample files..."

temp_dir="$(mktemp -d "${TMPDIR:-/tmp}/agentops-control-tower-html-demo.XXXXXX")"
trap 'rm -rf "${temp_dir}"' EXIT

create_agentops_demo_dataset "${temp_dir}"

html_report="${temp_dir}/exports/agentops-report.html"

uv run agentops-control-tower export-report \
  --format html \
  --run-history "${AGENTOPS_DEMO_RUN_HISTORY}" \
  --approval-requests "${AGENTOPS_DEMO_APPROVALS}" \
  --report "${AGENTOPS_DEMO_REPORT_REVIEW}" \
  --tool-evidence "${AGENTOPS_DEMO_TOOL_NOT_READY}" \
  --guardrail-output "${AGENTOPS_DEMO_GUARDRAIL_BLOCKED}" \
  --output "${html_report}"

echo "output_path=${html_report}"
echo "first_heading=$(grep -m 1 '<h1>' "${html_report}" | sed 's/^[[:space:]]*//')"
echo "file_size_bytes=$(wc -c < "${html_report}" | tr -d ' ')"
echo "workflow_records=3"
echo "approval_records=3"
echo "generated_reports=2"
echo "main_report=$(basename "${AGENTOPS_DEMO_REPORT_REVIEW}")"
echo "comparison_report=$(basename "${AGENTOPS_DEMO_REPORT_HEALTHY}")"
echo "note=HTML report is a local file artifact and uses one Markdown report path per CLI command."
