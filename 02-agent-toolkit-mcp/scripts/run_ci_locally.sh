#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$(cd "${PROJECT_ROOT}/.." && pwd)"
MCP_SERVER_ROOT="${PROJECT_ROOT}/mcp-server"
PROJECT_1_PATH="${REPO_ROOT}/01-ai-marketing-ops-agent"

export UV_CACHE_DIR="${UV_CACHE_DIR:-${TMPDIR:-/tmp}/agent-toolkit-mcp-uv-cache}"

echo "Running Project 2 scaffold checks..."
"${PROJECT_ROOT}/scripts/run_checks.sh"

echo
echo "Running Project 2 MCP server checks..."
"${PROJECT_ROOT}/scripts/run_mcp_checks.sh"

echo
echo "Validating Project 2 shell script syntax..."
bash -n "${PROJECT_ROOT}"/scripts/*.sh

echo
echo "Running Project 2 CLI smoke checks..."
cd "${MCP_SERVER_ROOT}"
uv run agent-toolkit-mcp --help
uv run agent-toolkit-mcp generate-demo-brief "${PROJECT_1_PATH}" --pretty
uv run agent-toolkit-mcp check-runtime-clean "${PROJECT_1_PATH}" --pretty

echo
echo "Project 2 local CI checks passed."
