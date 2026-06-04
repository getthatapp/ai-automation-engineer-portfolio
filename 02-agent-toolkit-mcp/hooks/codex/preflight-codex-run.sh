#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REPO_ROOT="$(cd "${PROJECT_ROOT}/.." && pwd)"

branch_name="$(git -C "${REPO_ROOT}" branch --show-current)"
echo "Current branch: ${branch_name:-unknown}"

if [[ "${branch_name}" == "main" && "${ALLOW_MAIN:-false}" != "true" ]]; then
  echo "Refusing to run on main. Set ALLOW_MAIN=true only for an explicitly approved exception." >&2
  exit 1
fi

if [[ -n "$(git -C "${REPO_ROOT}" status --short)" ]]; then
  if [[ "${STRICT_WORKTREE:-false}" == "true" ]]; then
    echo "Worktree is dirty and STRICT_WORKTREE=true." >&2
    git -C "${REPO_ROOT}" status --short >&2
    exit 1
  fi
  echo "Warning: worktree has existing changes. Review them before implementation." >&2
  git -C "${REPO_ROOT}" status --short >&2
else
  echo "Worktree is clean."
fi

if [[ -n "${PROMPT_HISTORY_FILE:-}" ]]; then
  "${PROJECT_ROOT}/hooks/shared/check-prompt-history-updated.sh"
else
  echo "PROMPT_HISTORY_FILE is not set; skipping prompt-history structure check."
fi

echo "Recommended Codex mode: workspace-write with sandboxing and approval-aware escalation."
echo "Preflight guardrail passed."
