#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REPO_ROOT="$(cd "${PROJECT_ROOT}/.." && pwd)"

echo "Running Claude Code post-tool-use audit example..."
git -C "${REPO_ROOT}" diff --check
bash -n "${PROJECT_ROOT}"/scripts/*.sh
find "${PROJECT_ROOT}/hooks" -name "*.sh" -exec bash -n {} \;
"${PROJECT_ROOT}/hooks/shared/check-no-secrets.sh"

echo "Claude Code post-tool-use audit passed."
