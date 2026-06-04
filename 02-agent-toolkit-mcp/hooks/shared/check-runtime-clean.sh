#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REPO_ROOT="$(cd "${PROJECT_ROOT}/.." && pwd)"
PROJECT_1_PATH="${PROJECT_1_PATH:-${REPO_ROOT}/01-ai-marketing-ops-agent}"
MCP_SERVER_ROOT="${PROJECT_ROOT}/mcp-server"

export UV_CACHE_DIR="${UV_CACHE_DIR:-${TMPDIR:-/tmp}/agent-toolkit-mcp-uv-cache}"

echo "Checking Project 1 runtime artifacts read-only..."
echo "Project 1 path: ${PROJECT_1_PATH}"

cd "${MCP_SERVER_ROOT}"
uv run agent-toolkit-mcp check-runtime-clean "${PROJECT_1_PATH}" --pretty

echo "Project 1 runtime artifact check passed."
