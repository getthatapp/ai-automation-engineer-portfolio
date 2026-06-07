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
  "docs/prompt-history/milestone-02-ingestion-models.md"
  "docs/prompt-history/milestone-03-summaries-timeline.md"
  "docs/prompt-history/milestone-04-cli-report-export.md"
  "examples/README.md"
  "examples/project-1-run-history/README.md"
  "examples/project-2-tool-evidence/README.md"
  "pyproject.toml"
  "scripts/run_checks.sh"
  "scripts/run_cli_demo.sh"
  "scripts/run_ingestion_demo.sh"
  "scripts/run_summary_demo.sh"
  "src/agentops_control_tower/__init__.py"
  "src/agentops_control_tower/cli.py"
  "src/agentops_control_tower/errors.py"
  "src/agentops_control_tower/ingestion.py"
  "src/agentops_control_tower/models.py"
  "src/agentops_control_tower/parsers.py"
  "src/agentops_control_tower/reporting.py"
  "src/agentops_control_tower/sanitization.py"
  "src/agentops_control_tower/summaries.py"
  "src/agentops_control_tower/timeline.py"
  "tests/test_cli.py"
  "tests/test_ingestion.py"
  "tests/test_reporting.py"
  "tests/test_summaries_timeline.py"
)

for path in "${required_files[@]}"; do
  if [[ ! -f "${path}" ]]; then
    echo "Missing required file: ${path}" >&2
    exit 1
  fi
done

echo "Validating Project 3 shell script syntax..."
bash -n scripts/*.sh

echo "Running Project 3 Python tests..."
uv run pytest

echo "Running Project 3 lint checks..."
uv run ruff check .

echo "Running Project 3 type checks..."
uv run mypy src

echo "Checking repository diff whitespace..."
git -C "${PROJECT_ROOT}/.." diff --check

echo
echo "Project 3 structure:"
find . \
  \( -path "*/.venv/*" -o -path "*/.pytest_cache/*" -o -path "*/.mypy_cache/*" -o -path "*/.ruff_cache/*" -o -path "*/__pycache__/*" \) -prune \
  -o -maxdepth 4 -type f -print | sort

echo
echo "Project 3 checks passed."
