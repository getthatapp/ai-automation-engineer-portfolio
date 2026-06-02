#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

echo "Running the Project 1 CI mirror from $PROJECT_DIR"
echo

echo "1/7 uv sync"
uv sync

echo
echo "2/7 Playwright Chromium"
uv run playwright install chromium

echo
echo "3/7 pytest"
uv run pytest

echo
echo "4/7 ruff"
uv run ruff check .

echo
echo "5/7 mypy"
uv run mypy src

echo
echo "6/7 Docker Compose config"
docker compose config

echo
echo "7/7 shell script syntax"
for script in scripts/*.sh; do
  bash -n "$script"
  echo "OK: $script"
done

echo
echo "Local CI mirror passed."
