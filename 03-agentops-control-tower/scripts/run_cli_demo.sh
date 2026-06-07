#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${PROJECT_ROOT}"

echo "Running local AgentOps CLI demo with temporary sample files..."

temp_dir="$(mktemp -d "${TMPDIR:-/tmp}/agentops-control-tower-cli-demo.XXXXXX")"
trap 'rm -rf "${temp_dir}"' EXIT

run_history="${temp_dir}/workflow-runs.jsonl"
approvals="${temp_dir}/approval-requests.jsonl"
report="${temp_dir}/daily-marketing-report-demo.md"
tool_evidence="${temp_dir}/tool-evidence.json"
guardrail="${temp_dir}/guardrail.txt"
exported_report="${temp_dir}/exports/agentops-report.md"

printf '%s\n' '{"critical_finding_count":0,"duration_seconds":3.0,"finished_at":"2026-05-28T12:00:03+00:00","finding_count":1,"human_review_required":false,"run_id":"daily-marketing-report-demo","snapshot_count":2,"started_at":"2026-05-28T12:00:00+00:00","status":"succeeded","task_error_count":0,"workflow_name":"daily_marketing_report"}' > "${run_history}"
printf '%s\n' '{"approval_id":"approval-demo","created_at":"2026-05-28T12:01:00+00:00","risk_level":"high","run_id":"daily-marketing-report-demo","source":"deterministic_finding","source_reference":"cmp-demo:negative_roi","status":"pending","title":"Review campaign"}' > "${approvals}"
cat > "${report}" <<'EOF'
# Daily Marketing Operations Report

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
EOF
printf '%s\n' '{"ready":true,"status":"ok","tool_name":"check_runtime_clean"}' > "${tool_evidence}"
printf '%s\n' "guardrail checks passed clean" > "${guardrail}"

source_args=(
  "--run-history" "${run_history}"
  "--approval-requests" "${approvals}"
  "--report" "${report}"
  "--tool-evidence" "${tool_evidence}"
  "--guardrail-output" "${guardrail}"
)

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
