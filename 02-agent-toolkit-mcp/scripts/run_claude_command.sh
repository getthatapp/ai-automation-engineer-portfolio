#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMMAND_NAME="${1:-}"

if [[ -z "${COMMAND_NAME}" ]]; then
  echo "Usage: $0 <command-name>"
  echo
  echo "Available Claude Code commands:"
  find "${PROJECT_ROOT}/claude-commands" -maxdepth 1 -type f -name "*.md" -exec basename {} .md \; | sort
  exit 1
fi

COMMAND_PATH="${PROJECT_ROOT}/claude-commands/${COMMAND_NAME}.md"

if [[ ! -f "${COMMAND_PATH}" ]]; then
  echo "Claude Code command not found: ${COMMAND_NAME}" >&2
  echo
  echo "Available Claude Code commands:" >&2
  find "${PROJECT_ROOT}/claude-commands" -maxdepth 1 -type f -name "*.md" -exec basename {} .md \; | sort >&2
  exit 1
fi

echo "Claude Code command template: ${COMMAND_PATH}"
echo
sed -n '1,240p' "${COMMAND_PATH}"

