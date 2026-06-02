#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${PROJECT_ROOT}"

echo "Checking Project 2 scaffold files..."

required_files=(
  "README.md"
  "AGENTS.md"
  "CLAUDE.md"
  "docs/ARCHITECTURE.md"
  "docs/CODEX_USAGE.md"
  "docs/CLAUDE_CODE_USAGE.md"
  "docs/SAFETY_MODEL.md"
  "docs/ROADMAP.md"
  "codex-prompts/review-workflow.md"
  "codex-prompts/generate-runbook.md"
  "codex-prompts/fix-ci-failure.md"
  "claude-commands/review-workflow.md"
  "claude-commands/generate-runbook.md"
  "claude-commands/fix-ci-failure.md"
  "skills/workflow-review/SKILL.md"
  "skills/mcp-tool-design/SKILL.md"
  "skills/runbook-writer/SKILL.md"
  "scripts/run_codex_prompt.sh"
  "scripts/run_claude_command.sh"
  "scripts/run_checks.sh"
  "examples/project-1-marketing-ops/README.md"
)

for path in "${required_files[@]}"; do
  if [[ ! -f "${path}" ]]; then
    echo "Missing required file: ${path}" >&2
    exit 1
  fi
done

echo "Validating shell script syntax..."
bash -n scripts/*.sh

echo
echo "Project 2 structure:"
find . -maxdepth 3 -type f | sort

echo
echo "Project 2 scaffold checks passed."

