#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROMPT_HISTORY_FILE="${PROMPT_HISTORY_FILE:-${PROJECT_ROOT}/docs/prompt-history/milestone-08-dual-agent-guardrails.md}"
export PROMPT_HISTORY_FILE

echo "Running shared no-secrets guardrail..."
"${PROJECT_ROOT}/hooks/shared/check-no-secrets.sh"

echo
echo "Running prompt-history guardrail..."
"${PROJECT_ROOT}/hooks/shared/check-prompt-history-updated.sh"

echo
echo "Validating Project 2 script syntax..."
bash -n "${PROJECT_ROOT}"/scripts/*.sh

echo
echo "Validating hook and guardrail script syntax..."
find "${PROJECT_ROOT}/hooks" -name "*.sh" -exec bash -n {} \;

echo
echo "Running Codex post-run audit guardrail..."
"${PROJECT_ROOT}/hooks/codex/postrun-codex-audit.sh"

echo
echo "Project 2 guardrail checks passed."
