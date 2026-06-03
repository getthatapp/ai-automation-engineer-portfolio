#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$(cd "${PROJECT_ROOT}/.." && pwd)"
PROJECT_1_PATH="${1:-${REPO_ROOT}/01-ai-marketing-ops-agent}"
MCP_SERVER_PATH="${PROJECT_ROOT}/mcp-server"

if [[ ! -d "${PROJECT_1_PATH}" ]]; then
  echo "Project 1 directory not found: ${PROJECT_1_PATH}" >&2
  exit 1
fi

if [[ ! -d "${MCP_SERVER_PATH}" ]]; then
  echo "Project 2 MCP server directory not found: ${MCP_SERVER_PATH}" >&2
  exit 1
fi

if [[ ! -f "${PROJECT_1_PATH}/README.md" ]]; then
  echo "Expected Project 1 README is missing: ${PROJECT_1_PATH}/README.md" >&2
  exit 1
fi

PYTHON_BIN="${MCP_SERVER_PATH}/.venv/bin/python"
if [[ ! -x "${PYTHON_BIN}" ]]; then
  echo "MCP server virtualenv not found: ${PYTHON_BIN}" >&2
  echo "Run ${PROJECT_ROOT}/scripts/run_mcp_checks.sh once to prepare the local environment." >&2
  exit 1
fi

cd "${MCP_SERVER_PATH}"

echo "Project 2 deterministic local tool registry:"
PYTHONPATH="${MCP_SERVER_PATH}/src" "${PYTHON_BIN}" -m agent_toolkit_mcp.server

echo
echo "Project 1 path:"
echo "${PROJECT_1_PATH}"

echo
echo "Running read-only Project 1 demo readiness and runtime artifact checks..."
PROJECT_1_PATH="${PROJECT_1_PATH}" \
PYTHONPATH="${MCP_SERVER_PATH}/src" \
"${PYTHON_BIN}" - <<'PY'
from __future__ import annotations

import os
from pathlib import Path

from agent_toolkit_mcp.tools import check_runtime_clean, generate_demo_brief

project_path = Path(os.environ["PROJECT_1_PATH"])
for result in (generate_demo_brief(project_path), check_runtime_clean(project_path)):
    print(result.model_dump_json(indent=2))
PY

echo
echo "Next steps:"
echo "- Run a full read-only artifact review:"
echo "  ${PROJECT_ROOT}/scripts/run_project1_tool_review.sh \"${PROJECT_1_PATH}\""
echo "- Preview Codex prompt templates:"
echo "  ${PROJECT_ROOT}/scripts/run_codex_prompt.sh inspect-project1-runtime"
echo "  ${PROJECT_ROOT}/scripts/run_codex_prompt.sh review-project1-report"
echo "  ${PROJECT_ROOT}/scripts/run_codex_prompt.sh summarize-project1-demo-readiness"
echo "- Preview Claude Code command templates:"
echo "  ${PROJECT_ROOT}/scripts/run_claude_command.sh inspect-project1-runtime"
echo "  ${PROJECT_ROOT}/scripts/run_claude_command.sh review-project1-report"
echo "  ${PROJECT_ROOT}/scripts/run_claude_command.sh summarize-project1-demo-readiness"
echo
echo "This demo is local-only, read-only and does not call external services."
