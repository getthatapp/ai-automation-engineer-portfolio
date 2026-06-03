#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$(cd "${PROJECT_ROOT}/.." && pwd)"
PROJECT_1_PATH="${1:-${REPO_ROOT}/01-ai-marketing-ops-agent}"
MCP_SERVER_PATH="${PROJECT_ROOT}/mcp-server"
REPORT_PATH="${2:-}"
RUN_HISTORY_PATH="${PROJECT_1_PATH}/run-history/workflow-runs.jsonl"
APPROVALS_PATH="${PROJECT_1_PATH}/approval-requests/approval-requests.jsonl"

if [[ ! -d "${PROJECT_1_PATH}" ]]; then
  echo "Project 1 directory not found: ${PROJECT_1_PATH}" >&2
  exit 1
fi

if [[ ! -d "${MCP_SERVER_PATH}" ]]; then
  echo "Project 2 MCP server directory not found: ${MCP_SERVER_PATH}" >&2
  exit 1
fi

if [[ -z "${REPORT_PATH}" ]]; then
  REPORT_PATH="$(find "${PROJECT_1_PATH}/reports" -maxdepth 1 -type f -name 'daily-marketing-report-*.md' 2>/dev/null | sort | tail -n 1 || true)"
fi

PYTHON_BIN="${MCP_SERVER_PATH}/.venv/bin/python"
if [[ ! -x "${PYTHON_BIN}" ]]; then
  echo "MCP server virtualenv not found: ${PYTHON_BIN}" >&2
  echo "Run ${PROJECT_ROOT}/scripts/run_mcp_checks.sh once to prepare the local environment." >&2
  exit 1
fi

cd "${MCP_SERVER_PATH}"

echo "Project 1 deterministic tool review"
echo "Project path: ${PROJECT_1_PATH}"
echo

if [[ -n "${REPORT_PATH}" ]]; then
  if [[ ! -f "${REPORT_PATH}" ]]; then
    echo "Report path was provided but does not exist: ${REPORT_PATH}" >&2
    exit 1
  fi
  echo "Report path: ${REPORT_PATH}"
else
  echo "Report path: not found under ${PROJECT_1_PATH}/reports"
fi

if [[ -f "${RUN_HISTORY_PATH}" ]]; then
  echo "Run history path: ${RUN_HISTORY_PATH}"
else
  echo "Run history path: missing (${RUN_HISTORY_PATH})"
fi

if [[ -f "${APPROVALS_PATH}" ]]; then
  echo "Approval queue path: ${APPROVALS_PATH}"
else
  echo "Approval queue path: missing (${APPROVALS_PATH})"
fi

echo
echo "Running read-only deterministic checks..."
PROJECT_1_PATH="${PROJECT_1_PATH}" \
REPORT_PATH="${REPORT_PATH}" \
RUN_HISTORY_PATH="${RUN_HISTORY_PATH}" \
APPROVALS_PATH="${APPROVALS_PATH}" \
PYTHONPATH="${MCP_SERVER_PATH}/src" \
"${PYTHON_BIN}" - <<'PY'
from __future__ import annotations

import os
from pathlib import Path

from agent_toolkit_mcp.tools import (
    check_runtime_clean,
    generate_demo_brief,
    list_pending_approvals,
    read_run_history,
    validate_report,
)

project_path = Path(os.environ["PROJECT_1_PATH"])
report_path = os.environ["REPORT_PATH"]
run_history_path = Path(os.environ["RUN_HISTORY_PATH"])
approvals_path = Path(os.environ["APPROVALS_PATH"])

results = [
    ("generate_demo_brief", generate_demo_brief(project_path)),
    ("check_runtime_clean", check_runtime_clean(project_path)),
    ("read_run_history", read_run_history(run_history_path, limit=5)),
    ("list_pending_approvals", list_pending_approvals(approvals_path)),
]

if report_path:
    results.insert(0, ("validate_report", validate_report(Path(report_path))))

for tool_name, result in results:
    print(f"## {tool_name}")
    print(result.model_dump_json(indent=2))
    print()
PY

echo "Review guidance:"
echo "- Treat missing report, run history or approval files as missing evidence, not proof of success."
echo "- Use pending approvals as human-review work items, not approved actions."
echo "- Use run history only for recorded local workflow runs."
echo "- Do not infer external delivery, real customer impact or production status from local artifacts."
echo
echo "This review is local-only, read-only and does not call external services."
