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
  "docs/prompt-history/README.md"
  "docs/prompt-history/TEMPLATE.md"
  "docs/prompt-history/milestone-02-mcp-server.md"
  "docs/prompt-history/milestone-03-agent-integration.md"
  "docs/prompt-history/milestone-04-runtime-config.md"
  "docs/runtime/MCP_RUNTIME_CONFIGURATION.md"
  "docs/runtime/CODEX_PERMISSION_PROFILES.md"
  "docs/runtime/CLAUDE_CODE_PERMISSION_PROFILES.md"
  "docs/runtime/LOCAL_ONLY_SECURITY_BOUNDARIES.md"
  "docs/runtime/TROUBLESHOOTING.md"
  "codex-prompts/review-workflow.md"
  "codex-prompts/generate-runbook.md"
  "codex-prompts/fix-ci-failure.md"
  "codex-prompts/inspect-project1-runtime.md"
  "codex-prompts/review-project1-report.md"
  "codex-prompts/summarize-project1-demo-readiness.md"
  "claude-commands/review-workflow.md"
  "claude-commands/generate-runbook.md"
  "claude-commands/fix-ci-failure.md"
  "claude-commands/inspect-project1-runtime.md"
  "claude-commands/review-project1-report.md"
  "claude-commands/summarize-project1-demo-readiness.md"
  "skills/workflow-review/SKILL.md"
  "skills/mcp-tool-design/SKILL.md"
  "skills/runbook-writer/SKILL.md"
  "scripts/run_codex_prompt.sh"
  "scripts/run_claude_command.sh"
  "scripts/run_checks.sh"
  "scripts/run_mcp_checks.sh"
  "scripts/demo_mcp_tools.sh"
  "scripts/run_project1_tool_review.sh"
  "scripts/show_permission_profiles.sh"
  "examples/project-1-marketing-ops/README.md"
  "examples/project-1-marketing-ops/TOOL_REVIEW_FLOW.md"
  "examples/project-1-marketing-ops/SAMPLE_AGENT_REVIEW.md"
  "examples/runtime-config/codex-read-only-example.md"
  "examples/runtime-config/codex-workspace-write-example.md"
  "examples/runtime-config/claude-code-read-only-example.md"
  "examples/runtime-config/claude-code-approval-required-example.md"
  "examples/runtime-config/mcp-server-local-example.md"
  "mcp-server/README.md"
  "mcp-server/pyproject.toml"
  "mcp-server/src/agent_toolkit_mcp/__init__.py"
  "mcp-server/src/agent_toolkit_mcp/server.py"
  "mcp-server/src/agent_toolkit_mcp/tools.py"
  "mcp-server/src/agent_toolkit_mcp/models.py"
  "mcp-server/src/agent_toolkit_mcp/errors.py"
  "mcp-server/src/agent_toolkit_mcp/path_safety.py"
  "mcp-server/tests/test_tools.py"
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
find . \
  \( -path "*/.venv/*" -o -path "*/.pytest_cache/*" -o -path "*/.mypy_cache/*" -o -path "*/.ruff_cache/*" -o -path "*/__pycache__/*" \) -prune \
  -o -maxdepth 4 -type f -print | sort

echo
echo "Project 2 scaffold checks passed."
echo "Run ./scripts/run_mcp_checks.sh for MCP server tests, linting and typing."
