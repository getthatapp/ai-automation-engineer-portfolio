#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROMPT_NAME="${1:-}"

if [[ -z "${PROMPT_NAME}" ]]; then
  echo "Usage: $0 <prompt-name>"
  echo
  echo "Available Codex prompts:"
  find "${PROJECT_ROOT}/codex-prompts" -maxdepth 1 -type f -name "*.md" -exec basename {} .md \; | sort
  exit 1
fi

PROMPT_PATH="${PROJECT_ROOT}/codex-prompts/${PROMPT_NAME}.md"

if [[ ! -f "${PROMPT_PATH}" ]]; then
  echo "Codex prompt not found: ${PROMPT_NAME}" >&2
  echo
  echo "Available Codex prompts:" >&2
  find "${PROJECT_ROOT}/codex-prompts" -maxdepth 1 -type f -name "*.md" -exec basename {} .md \; | sort >&2
  exit 1
fi

echo "Codex prompt template: ${PROMPT_PATH}"
echo
sed -n '1,240p' "${PROMPT_PATH}"

