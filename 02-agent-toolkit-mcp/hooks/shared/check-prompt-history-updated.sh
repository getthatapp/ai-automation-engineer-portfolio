#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REPO_ROOT="$(cd "${PROJECT_ROOT}/.." && pwd)"
DEFAULT_PROMPT_HISTORY_FILE="${PROJECT_ROOT}/docs/prompt-history/milestone-08-dual-agent-guardrails.md"
PROMPT_HISTORY_FILE="${PROMPT_HISTORY_FILE:-${DEFAULT_PROMPT_HISTORY_FILE}}"

if [[ "${PROMPT_HISTORY_FILE}" != /* ]]; then
  PROMPT_HISTORY_FILE="${REPO_ROOT}/${PROMPT_HISTORY_FILE}"
fi

echo "Checking prompt-history file: ${PROMPT_HISTORY_FILE}"

if [[ ! -f "${PROMPT_HISTORY_FILE}" ]]; then
  echo "Prompt-history file is missing: ${PROMPT_HISTORY_FILE}" >&2
  exit 1
fi

required_patterns=(
  '^## (Full Prompt|Prompt Used)$'
  '^## Expected Verification$'
  '^## Result Summary$'
  '^## Verification Results$'
)

for pattern in "${required_patterns[@]}"; do
  if ! grep -Eq "${pattern}" "${PROMPT_HISTORY_FILE}"; then
    echo "Prompt-history file is missing required section pattern: ${pattern}" >&2
    exit 1
  fi
done

echo "Prompt-history guardrail passed."
