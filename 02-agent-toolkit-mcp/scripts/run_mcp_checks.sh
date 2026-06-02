#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export UV_CACHE_DIR="${UV_CACHE_DIR:-${TMPDIR:-/tmp}/agent-toolkit-mcp-uv-cache}"
cd "${PROJECT_ROOT}/mcp-server"

echo "Running Project 2 MCP server tests..."
uv run pytest

echo
echo "Running Project 2 MCP server lint checks..."
uv run ruff check .

echo
echo "Running Project 2 MCP server type checks..."
uv run mypy src

echo
echo "Validating Project 2 shell script syntax..."
bash -n ../scripts/*.sh

echo
echo "Project 2 MCP checks passed."
