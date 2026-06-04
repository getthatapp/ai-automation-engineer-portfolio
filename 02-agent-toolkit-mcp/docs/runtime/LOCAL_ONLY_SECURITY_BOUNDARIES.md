# Local-Only Security Boundaries

Project 2 is currently a local toolkit. It helps agents inspect and summarize
Project 1 artifacts without external side effects.

## Boundaries

- Tools inspect local filesystem paths supplied by the user or scripts.
- Project-level checks stay under the provided Project 1 directory.
- Symlinks are resolved before path validation; links that resolve outside a
  validated project path are rejected and reported.
- JSONL-reading tools sanitize secret-like keys and obvious bearer/API-token
  values.
- Adapter scripts report generated files but do not remove them.
- The `agent-toolkit-mcp` CLI wraps the same read-only tools and only prints
  JSON evidence plus process exit codes.
- Prompt and command templates are instructions, not external integrations.

## Not Allowed

- Hardcoded credentials.
- Real Slack, Telegram, email or other external service calls.
- Destructive runtime cleanup.
- Project 1 code or behavior changes during Project 2 runtime review.
- Claims that external MCP transport is deployed.
- Claims that the local CLI is a deployed MCP service.
- Claims that pending approvals are approved actions.

## Evidence Rules

Agents should use deterministic local outputs as evidence and label missing
artifacts as missing evidence. They should not invent:

- reports;
- workflow run records;
- approval decisions;
- external notification delivery;
- production deployment status;
- real customer or business impact.

## Safe Project 1 Artifact Scope

Current Project 2 scripts may inspect:

- `01-ai-marketing-ops-agent/reports/`
- `01-ai-marketing-ops-agent/run-history/workflow-runs.jsonl`
- `01-ai-marketing-ops-agent/approval-requests/approval-requests.jsonl`
- expected Project 1 docs, scripts and workflow files used by
  `generate_demo_brief`.

They must not mutate those artifacts.

## Hardened Output Boundaries

Milestone 5 adds richer typed outputs while preserving the same local boundary:

- report validation warnings and explicit summary extraction;
- total JSONL record counts and malformed-line reporting;
- pending approval counts without full sensitive payloads;
- runtime artifact counts by type;
- structured demo readiness checks.

These outputs are evidence aids. They must not be treated as production
telemetry or proof of external service delivery.
