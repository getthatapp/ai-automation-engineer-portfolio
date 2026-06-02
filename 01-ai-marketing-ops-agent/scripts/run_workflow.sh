#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

export MARKETING_PANEL_BASE_URL="${MARKETING_PANEL_BASE_URL:-http://localhost:8000}"
export MARKETING_PANEL_USERNAME="${MARKETING_PANEL_USERNAME:-demo@example.com}"
export MARKETING_PANEL_PASSWORD="${MARKETING_PANEL_PASSWORD:-local-password}"
export MARKETING_PANEL_2FA_CODE="${MARKETING_PANEL_2FA_CODE:-000000}"
export CAMPAIGN_API_BASE_URL="${CAMPAIGN_API_BASE_URL:-http://localhost:8001}"
export ANALYTICS_GRAPHQL_URL="${ANALYTICS_GRAPHQL_URL:-http://localhost:8002/graphql}"
export PROJECT_MANAGEMENT_API_BASE_URL="${PROJECT_MANAGEMENT_API_BASE_URL:-http://localhost:8003}"
export LLM_INTERPRETATION_ENABLED="${LLM_INTERPRETATION_ENABLED:-false}"
export LLM_PROVIDER="${LLM_PROVIDER:-mock}"
export LLM_MODEL="${LLM_MODEL:-deterministic-marketing-interpreter}"

echo "Running daily marketing report workflow."
echo "Expected mock services:"
echo "  marketing panel: $MARKETING_PANEL_BASE_URL"
echo "  campaign API: $CAMPAIGN_API_BASE_URL"
echo "  analytics GraphQL: $ANALYTICS_GRAPHQL_URL"
echo

uv run python -m marketing_ops_agent.workflows.daily_marketing_report

echo
echo "Workflow finished."

latest_report="$(find reports -maxdepth 1 -type f -name '*.md' -print 2>/dev/null | sort | tail -n 1 || true)"
if [[ -n "$latest_report" ]]; then
  echo "Latest report: $latest_report"
  echo "Inspect it with: sed -n '1,220p' '$latest_report'"
else
  echo "No Markdown report found under reports/."
fi

if [[ -f run-history/workflow-runs.jsonl ]]; then
  echo
  echo "Latest run record:"
  tail -n 1 run-history/workflow-runs.jsonl
  echo "Inspect recent runs with: tail -n 5 run-history/workflow-runs.jsonl"
fi

if [[ -f approval-requests/approval-requests.jsonl ]]; then
  echo
  echo "Approval requests exist. Inspect them with:"
  echo "tail -n 20 approval-requests/approval-requests.jsonl"
else
  echo
  echo "No approval request file exists yet."
fi
