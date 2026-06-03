# Local-Only Security Boundaries

Project 2 is currently a local toolkit. It helps agents inspect and summarize
Project 1 artifacts without external side effects.

## Boundaries

- Tools inspect local filesystem paths supplied by the user or scripts.
- Project-level checks stay under the provided Project 1 directory.
- JSONL-reading tools sanitize secret-like keys and obvious bearer/API-token
  values.
- Adapter scripts report generated files but do not remove them.
- Prompt and command templates are instructions, not external integrations.

## Not Allowed

- Hardcoded credentials.
- Real Slack, Telegram, email or other external service calls.
- Destructive runtime cleanup.
- Project 1 code or behavior changes during Project 2 runtime review.
- Claims that external MCP transport is deployed.
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
