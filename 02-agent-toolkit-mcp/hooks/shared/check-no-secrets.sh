#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REPO_ROOT="$(cd "${PROJECT_ROOT}/.." && pwd)"

# Conservative patterns for obvious assignments or well-known token prefixes.
# This is not a replacement for a dedicated secret scanner.
SECRET_ASSIGNMENT_PATTERN='(api[_-]?key|authorization|bearer[_-]?token|access[_-]?token|secret|password|credential)[[:space:]]*[:=][[:space:]]*["'\'']?[A-Za-z0-9_./+=:@-]{12,}'
TOKEN_VALUE_PATTERN='(sk-[A-Za-z0-9_-]{20,}|xox[baprs]-[A-Za-z0-9-]{20,}|gh[pousr]_[A-Za-z0-9_]{20,})'
SAFE_DEMO_PATTERN='MARKETING_PANEL_PASSWORD=local-password|MARKETING_PANEL_2FA_CODE=000000|demo@example\.com'

echo "Checking selected files for obvious secret-like patterns..."

find_roots=(
  "${REPO_ROOT}/README.md"
  "${REPO_ROOT}/AGENTS.md"
  "${REPO_ROOT}/docs/CODEX_HANDOFF_AI_AUTOMATION_PORTFOLIO.md"
  "${REPO_ROOT}/.github/workflows"
  "${PROJECT_ROOT}"
)

failed=0
while IFS= read -r -d '' file_path; do
  relative_path="${file_path#${REPO_ROOT}/}"
  if grep -Eiv "${SAFE_DEMO_PATTERN}" "${file_path}" | grep -Eiq "${SECRET_ASSIGNMENT_PATTERN}"; then
    echo "Potential secret assignment found: ${relative_path}" >&2
    failed=1
  fi
  if grep -Eiv "${SAFE_DEMO_PATTERN}" "${file_path}" | grep -Eiq "${TOKEN_VALUE_PATTERN}"; then
    echo "Potential token-like value found: ${relative_path}" >&2
    failed=1
  fi
done < <(
  find "${find_roots[@]}" \
    \( -path "*/.git/*" \
      -o -path "*/.venv/*" \
      -o -path "*/.mypy_cache/*" \
      -o -path "*/.pytest_cache/*" \
      -o -path "*/.ruff_cache/*" \
      -o -path "*/__pycache__/*" \
      -o -path "*/docs/prompt-history/*" \
      -o -path "*/mcp-server/uv.lock" \) -prune \
    -o -type f \
    \( -name "*.md" -o -name "*.sh" -o -name "*.yml" -o -name "*.yaml" -o -name "*.toml" \) \
    -print0
)

if [[ "${failed}" -ne 0 ]]; then
  echo "Secret guardrail failed. Review the reported files without printing secret values." >&2
  exit 1
fi

echo "No obvious secret-like patterns found in selected files."
