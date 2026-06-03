#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNTIME_DOCS="${PROJECT_ROOT}/docs/runtime"

echo "Project 2 local permission profiles"
echo
echo "1. read-only inspection"
echo "   Inspect docs and local Project 1 artifacts without file changes."
echo
echo "2. workspace-write development"
echo "   Make scoped Project 2 documentation, template and non-destructive script edits."
echo
echo "3. approval-required operations"
echo "   Require explicit human approval for branch operations, dependency resolution or elevated local commands."
echo
echo "4. blocked/destructive operation policy"
echo "   Destructive tools, credential insertion, Project 1 runtime mutation and real external calls are not supported."
echo
echo "Runtime docs:"
echo "- ${RUNTIME_DOCS}/MCP_RUNTIME_CONFIGURATION.md"
echo "- ${RUNTIME_DOCS}/CODEX_PERMISSION_PROFILES.md"
echo "- ${RUNTIME_DOCS}/CLAUDE_CODE_PERMISSION_PROFILES.md"
echo "- ${RUNTIME_DOCS}/LOCAL_ONLY_SECURITY_BOUNDARIES.md"
echo "- ${RUNTIME_DOCS}/TROUBLESHOOTING.md"
echo
echo "This script is read-only and does not call external services."
