#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

echo "Running Project 1 quality checks from $PROJECT_DIR"
echo

echo "1/3 pytest"
uv run pytest

echo
echo "2/3 ruff"
uv run ruff check .

echo
echo "3/3 mypy"
uv run mypy src

echo
echo "All checks passed."
