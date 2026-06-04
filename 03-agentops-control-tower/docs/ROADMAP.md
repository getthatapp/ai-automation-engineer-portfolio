# Roadmap

## Milestone 1 - Scaffold and Documentation

Status: **Complete**

Create the Project 3 folder, project guidance, architecture docs, observability
model docs, source documentation, examples and a local scaffold check script.

## Milestone 2 - Local Data Ingestion Models

Status: **Complete**

Define typed local models for workflow runs, approval requests, generated
reports, tool evidence and guardrail outcomes. Add deterministic parsers for
selected local artifacts without adding external integrations.

## Milestone 3 - Local AgentOps Summaries and Timeline

Status: **Complete**

Use the typed ingestion layer to build local summaries and a deterministic
AgentOps timeline for runs, approvals, report summaries and guardrail outcomes.

## Milestone 4 - Local Report Export or Dashboard-Ready CLI

Status: **Next**

Expose the local AgentOps summary and timeline through a reviewer-friendly CLI
or static export format without adding a frontend UI, database or service.

## Future Milestones

- Retry, failure and approval state summaries.
- Token and cost metadata summaries when available.
- Local dashboard or report surface.
- CI checks for Project 3.
- Final recruiter demo package and case study.

Future milestones must continue to avoid overclaiming real external AgentOps
deployment unless such deployment is actually implemented.
