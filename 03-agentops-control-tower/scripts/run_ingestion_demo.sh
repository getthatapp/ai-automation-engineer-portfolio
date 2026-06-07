#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${PROJECT_ROOT}"

# shellcheck source=scripts/demo_dataset.sh
source "${PROJECT_ROOT}/scripts/demo_dataset.sh"

echo "Running local AgentOps ingestion demo with richer temporary sample files..."

temp_dir="$(mktemp -d "${TMPDIR:-/tmp}/agentops-control-tower-demo.XXXXXX")"
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

from agentops_control_tower import ingest_local_agentops_sources

run_history, approvals, report, tool_evidence, guardrail = map(Path, sys.argv[1:])

result = ingest_local_agentops_sources(
    run_history_path=run_history,
    approval_requests_path=approvals,
    markdown_report_path=report,
    tool_evidence_json_path=tool_evidence,
    guardrail_output_text_path=guardrail,
)

print(f"records={result.record_count}")
print(f"warnings={len(result.warnings)}")
print(f"errors={len(result.errors)}")
print(f"ok={str(result.ok).lower()}")
PY

echo "workflow_records=3"
echo "approval_records=3"
echo "generated_reports=2"
echo "main_report=$(basename "${AGENTOPS_DEMO_REPORT_REVIEW}")"
echo "comparison_report=$(basename "${AGENTOPS_DEMO_REPORT_HEALTHY}")"
echo "tool_evidence_used=$(basename "${AGENTOPS_DEMO_TOOL_NOT_READY}")"
echo "guardrail_used=$(basename "${AGENTOPS_DEMO_GUARDRAIL_BLOCKED}")"
