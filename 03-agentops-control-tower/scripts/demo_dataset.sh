#!/usr/bin/env bash

create_agentops_demo_dataset() {
  local target_dir="$1"

  mkdir -p "${target_dir}"

  AGENTOPS_DEMO_RUN_HISTORY="${target_dir}/workflow-runs.jsonl"
  AGENTOPS_DEMO_APPROVALS="${target_dir}/approval-requests.jsonl"
  AGENTOPS_DEMO_REPORT_REVIEW="${target_dir}/daily-marketing-report-review.md"
  AGENTOPS_DEMO_REPORT_HEALTHY="${target_dir}/daily-marketing-report-healthy.md"
  AGENTOPS_DEMO_TOOL_READY="${target_dir}/tool-evidence-ready.json"
  AGENTOPS_DEMO_TOOL_NOT_READY="${target_dir}/tool-evidence-not-ready.json"
  AGENTOPS_DEMO_GUARDRAIL_PASSED="${target_dir}/guardrail-passed.txt"
  AGENTOPS_DEMO_GUARDRAIL_BLOCKED="${target_dir}/guardrail-blocked.txt"

  cat > "${AGENTOPS_DEMO_RUN_HISTORY}" <<'EOF'
{"approval_request_count":0,"critical_finding_count":0,"duration_seconds":4.0,"finished_at":"2026-05-28T12:00:04+00:00","finding_count":1,"human_review_required":false,"notification_status":"skipped","run_id":"run-20260528-success","snapshot_count":5,"started_at":"2026-05-28T12:00:00+00:00","status":"succeeded","task_error_count":0,"workflow_name":"daily_marketing_report"}
{"approval_request_count":2,"critical_finding_count":1,"duration_seconds":5.0,"finished_at":"2026-05-28T12:10:05+00:00","finding_count":3,"human_review_required":true,"notification_status":"pending_approval","run_id":"run-20260528-needs-approval","snapshot_count":5,"started_at":"2026-05-28T12:10:00+00:00","status":"needs_approval","task_error_count":0,"workflow_name":"daily_marketing_report"}
{"approval_request_count":1,"critical_finding_count":1,"duration_seconds":2.0,"failure_message":"Mock task provider returned validation failure.","failure_type":"task_creation_failed","finished_at":"2026-05-28T12:20:02+00:00","finding_count":2,"human_review_required":true,"notification_status":"not_sent","run_id":"run-20260528-failed","snapshot_count":4,"started_at":"2026-05-28T12:20:00+00:00","status":"failed","task_error_count":1,"workflow_name":"daily_marketing_report"}
EOF

  cat > "${AGENTOPS_DEMO_APPROVALS}" <<'EOF'
{"approval_id":"approval-high-pending","created_at":"2026-05-28T12:11:00+00:00","risk_level":"high","run_id":"run-20260528-needs-approval","source":"deterministic_finding","source_reference":"cmp-enterprise:negative_roi","status":"pending","title":"Review high-risk budget recommendation"}
{"approval_id":"approval-medium-approved","created_at":"2026-05-28T12:12:00+00:00","decision":{"approved_by":"reviewer","decided_at":"2026-05-28T12:14:00+00:00"},"risk_level":"medium","run_id":"run-20260528-success","source":"notification_summary","source_reference":"summary:weekly-health","status":"approved","title":"Approve weekly stakeholder summary"}
{"approval_id":"approval-high-rejected","created_at":"2026-05-28T12:13:00+00:00","decision":{"decided_at":"2026-05-28T12:15:00+00:00","rejected_by":"reviewer"},"risk_level":"high","run_id":"run-20260528-failed","source":"task_creation","source_reference":"task:pause-campaign","status":"rejected","title":"Reject unsafe campaign pause task"}
EOF

  cat > "${AGENTOPS_DEMO_REPORT_REVIEW}" <<'EOF'
# Daily Marketing Operations Report

Generated timestamp: 2026-05-28T12:30:00+00:00

## Executive Summary
- Campaigns processed: 5.
- Critical findings: 1.
- Warning findings: 3.
- Campaigns requiring human review: 2.

## Campaign Health Overview
Review-focused demo report with multiple campaign states.

## Critical Anomalies
One critical anomaly requires human review.

## Warning Anomalies
Three warning anomalies require monitoring.

## Data Quality Issues
No malformed local demo evidence is included.

## Human Review Required
Two campaigns require reviewer attention.

## Campaign Snapshot Table
Deterministic sample table omitted from parser-focused demo.

## Deterministic Recommended Actions
Review pending approvals before sending notifications.

## Limitations
Project 3 CLI currently accepts one Markdown report path per command.
EOF

  cat > "${AGENTOPS_DEMO_REPORT_HEALTHY}" <<'EOF'
# Daily Marketing Operations Report

Generated timestamp: 2026-05-28T13:30:00+00:00

## Executive Summary
- Campaigns processed: 4.
- Critical findings: 0.
- Warning findings: 1.
- Campaigns requiring human review: 0.

## Campaign Health Overview
Healthy comparison report for the richer local demo dataset.

## Critical Anomalies
No critical anomalies.

## Warning Anomalies
One warning anomaly requires monitoring.

## Data Quality Issues
No malformed local demo evidence is included.

## Human Review Required
No human review required.

## Campaign Snapshot Table
Deterministic sample table omitted from parser-focused demo.

## Deterministic Recommended Actions
Continue monitoring local workflow evidence.

## Limitations
Project 3 CLI currently accepts one Markdown report path per command.
EOF

  cat > "${AGENTOPS_DEMO_TOOL_READY}" <<'EOF'
{"ready":true,"status":"ok","tool_name":"check_runtime_clean"}
EOF
  cat > "${AGENTOPS_DEMO_TOOL_NOT_READY}" <<'EOF'
{"ready":false,"status":"needs_attention","tool_name":"generate_demo_brief","warnings":["stale report artifact detected in local evidence"]}
EOF

  printf '%s\n' "guardrail checks passed clean" > "${AGENTOPS_DEMO_GUARDRAIL_PASSED}"
  printf '%s\n' "blocked destructive command intent during local guardrail review" > "${AGENTOPS_DEMO_GUARDRAIL_BLOCKED}"
}
