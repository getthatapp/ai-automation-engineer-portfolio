#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${PROJECT_ROOT}"

echo "Checking Project 3 scaffold files..."

required_files=(
  "README.md"
  "AGENTS.md"
  "docs/ARCHITECTURE.md"
  "docs/ROADMAP.md"
  "docs/OBSERVABILITY_MODEL.md"
  "docs/DATA_SOURCES.md"
  "docs/SAFETY_MODEL.md"
  "docs/LOCAL_DEMO_PLAN.md"
  "docs/prompt-history/README.md"
  "docs/prompt-history/TEMPLATE.md"
  "docs/prompt-history/milestone-01-scaffold.md"
  "examples/README.md"
  "examples/project-1-run-history/README.md"
  "examples/project-2-tool-evidence/README.md"
  "scripts/run_checks.sh"
)

for path in "${required_files[@]}"; do
  if [[ ! -f "${path}" ]]; then
    echo "Missing required file: ${path}" >&2
    exit 1
  fi
done

echo "Validating Project 3 shell script syntax..."
bash -n scripts/*.sh

echo
echo "Project 3 structure:"
find . \
  \( -path "*/.venv/*" -o -path "*/.pytest_cache/*" -o -path "*/.mypy_cache/*" -o -path "*/.ruff_cache/*" -o -path "*/__pycache__/*" \) -prune \
  -o -maxdepth 4 -type f -print | sort

echo
echo "Project 3 scaffold checks passed."
