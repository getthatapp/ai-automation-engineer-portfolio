#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REPO_ROOT="$(cd "${PROJECT_ROOT}/.." && pwd)"

echo "Running Codex post-run audit checks..."
"${PROJECT_ROOT}/scripts/run_checks.sh"
"${PROJECT_ROOT}/scripts/run_mcp_checks.sh"
if [[ -x "${PROJECT_ROOT}/scripts/run_ci_locally.sh" ]]; then
  "${PROJECT_ROOT}/scripts/run_ci_locally.sh"
fi
bash -n "${PROJECT_ROOT}"/scripts/*.sh
find "${PROJECT_ROOT}/hooks" -name "*.sh" -exec bash -n {} \;
git -C "${REPO_ROOT}" diff --check
"${PROJECT_ROOT}/hooks/shared/check-no-secrets.sh"

echo "Codex post-run audit passed. No commit was created."
