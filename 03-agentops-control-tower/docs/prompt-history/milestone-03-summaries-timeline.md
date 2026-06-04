# Project 3 Milestone 3 - Local AgentOps Summaries and Timeline

Status: `Complete`
Branch: `feature/project-3-m03-summaries-timeline`

## Full Prompt

```text
Read the root AGENTS.md and docs/CODEX_HANDOFF_AI_AUTOMATION_PORTFOLIO.md first.
Then read:
- 03-agentops-control-tower/AGENTS.md
- 03-agentops-control-tower/README.md
- 03-agentops-control-tower/docs/ARCHITECTURE.md
- 03-agentops-control-tower/docs/ROADMAP.md
- 03-agentops-control-tower/docs/OBSERVABILITY_MODEL.md
- 03-agentops-control-tower/docs/DATA_SOURCES.md
- 03-agentops-control-tower/docs/SAFETY_MODEL.md
- 03-agentops-control-tower/docs/LOCAL_DEMO_PLAN.md
- 03-agentops-control-tower/docs/prompt-history/README.md
- 03-agentops-control-tower/docs/prompt-history/TEMPLATE.md
- 03-agentops-control-tower/docs/prompt-history/milestone-02-ingestion-models.md

Continue Project 3: 03-agentops-control-tower.

Milestone 3: local AgentOps summaries and timeline.

Branch:
feature/project-3-m03-summaries-timeline

Prompt history requirement:
Create or update:
03-agentops-control-tower/docs/prompt-history/milestone-03-summaries-timeline.md

The prompt-history file must include:
- title,
- status,
- branch,
- this full prompt,
- expected verification,
- result summary placeholder,
- verification result placeholder,
- commit / PR placeholder,
- notes.

After implementation, update the same prompt-history file with the actual result summary and verification results.

Current state:
- Project 1 is complete and portfolio-ready.
- Project 1 produces local workflow artifacts:
  - run-history/workflow-runs.jsonl
  - approval-requests/approval-requests.jsonl
  - reports/daily-marketing-report-*.md
- Project 2 is complete and portfolio-ready.
- Project 2 provides deterministic local MCP-style tools, CLI, guardrails, CI and demo docs.
- Project 3 Milestone 1 scaffold is complete.
- Project 3 Milestone 2 added local deterministic ingestion models and parsers.
- Project 3 can now parse:
  - Project 1 run-history JSONL
  - Project 1 approval requests JSONL
  - Project 1 Markdown reports
  - Project 2 CLI JSON evidence
  - Project 2 guardrail output text
- Project 3 does not yet provide normalized summaries, timeline events, dashboard-ready views or reporting.
- This milestone should build deterministic local summaries and timeline models on top of the ingestion layer.
- Do not modify Project 1 code.
- Do not modify Project 2 code unless only documentation links require it.
- Do not change Project 1 or Project 2 runtime behavior.
- Do not add frontend UI.
- Do not add external integrations.
- Do not call external APIs.
- Do not require secrets.
- Do not add database or scheduler yet.

Goal:
Implement deterministic local AgentOps summaries and timeline generation from the typed ingestion layer.

The new layer should convert ingested Project 1 and Project 2 evidence into reviewer-friendly, dashboard-ready summaries without implementing a UI yet.

Implement:

1. Add summary/timeline modules under:
   03-agentops-control-tower/src/agentops_control_tower/

Suggested files:
- timeline.py
- summaries.py

Update existing files only as needed:
- models.py
- __init__.py

2. Add typed models.

Suggested models:
- AgentOpsTimelineEvent
- AgentOpsTimeline
- WorkflowRunSummary
- ApprovalSummary
- ReportHealthSummary
- ToolEvidenceSummary
- GuardrailSummary
- AgentOpsSummary
- SummarySeverity enum if useful
- TimelineEventType enum if useful

3. Implement deterministic timeline generation.

Suggested function:
build_agentops_timeline(ingestion_result)

Behavior:
- Accept an IngestionResult from Milestone 2.
- Produce deterministic timeline events from available records.
- Include event types for:
  - workflow_run
  - approval_request
  - report_summary
  - tool_evidence
  - guardrail_evidence
  - ingestion_warning
  - ingestion_error
- Preserve stable ordering:
  - timestamped events sorted by timestamp ascending,
  - untimestamped events placed after timestamped events in deterministic source/type order,
  - stable tie-breaking by source type and identifier.
- Do not infer missing timestamps.
- Do not call LLM.
- Do not mutate files.

4. Implement deterministic summary generation.

Suggested function:
build_agentops_summary(ingestion_result)

Behavior:
- Count workflow runs by status.
- Count approvals by status.
- Count reports parsed and reports requiring human review if represented.
- Count ingestion warnings and errors.
- Count guardrail statuses.
- Count tool evidence records.
- Derive overall local health status deterministically:
  - error if ingestion errors exist
  - needs_attention if failed/blocked guardrails exist or human review/pending approvals exist
  - warning if warnings exist
  - healthy otherwise
- Include concise recommended local follow-up actions based only on deterministic data.
- Do not infer business facts that are not present.
- Do not call LLM.

5. Implement convenience aggregator.

Suggested function:
build_agentops_control_tower_view(...)

Behavior:
- Accept either:
  - an existing IngestionResult, or
  - the same optional local paths accepted by ingest_local_agentops_sources.
- Return a typed object containing:
  - ingestion result
  - summary
  - timeline
- This is still local-only and read-only.

6. Add tests.

Add tests for:
- timeline from workflow run records
- timeline from approval records
- timeline from report summaries
- timeline from tool evidence records
- timeline from guardrail evidence records
- warnings/errors becoming timeline events
- deterministic ordering with timestamps and without timestamps
- summary counts for workflow statuses
- summary counts for approval statuses
- summary overall status healthy
- summary overall status warning
- summary overall status needs_attention
- summary overall status error
- recommended actions from deterministic signals
- combined control tower view from an existing IngestionResult
- combined control tower view from local temporary source files
- no LLM/external calls

7. Add or update demo script:
- 03-agentops-control-tower/scripts/run_summary_demo.sh

Behavior:
- local-only
- read-only
- use temporary sample files or existing safe local sample artifacts
- run ingestion
- build summary and timeline
- print concise deterministic output:
  - overall status
  - counts
  - timeline event count
  - recommended actions
- no external APIs
- no secrets
- executable
- bash with set -euo pipefail

8. Update scripts:
- 03-agentops-control-tower/scripts/run_checks.sh

It should verify new files exist and run:
- pytest
- ruff
- mypy
- bash syntax checks
- git diff --check from repo root if practical

9. Documentation updates:
- 03-agentops-control-tower/README.md
- 03-agentops-control-tower/docs/ARCHITECTURE.md
- 03-agentops-control-tower/docs/ROADMAP.md
- 03-agentops-control-tower/docs/OBSERVABILITY_MODEL.md
- 03-agentops-control-tower/docs/DATA_SOURCES.md if useful
- 03-agentops-control-tower/docs/LOCAL_DEMO_PLAN.md
- docs/CODEX_HANDOFF_AI_AUTOMATION_PORTFOLIO.md
- root README.md only if useful and concise

10. Documentation should explain:
- what summaries exist
- what timeline events exist
- how the summary health status is derived
- what is not implemented yet
- that there is no dashboard/UI yet
- that this is local-only and deterministic
- that recommended actions are deterministic and not LLM-generated

Rules:
- Keep all docs in English.
- Keep all tools local and read-only.
- Do not mutate Project 1 files.
- Do not mutate Project 2 files.
- Do not delete generated runtime files.
- Do not add real credentials.
- Do not call external APIs.
- Do not hardcode secrets.
- Do not add frontend UI.
- Do not add database, scheduler or background service.
- Do not overclaim a deployed AgentOps platform.
- Keep scripts executable.
- Add Google-style docstrings to every new or modified Python function, method and class.
- Keep prompt history current.
- Keep tests deterministic.
- Avoid broad refactors unrelated to this milestone.

Expected verification:
Run:
- 03-agentops-control-tower/scripts/run_checks.sh
- 03-agentops-control-tower/scripts/run_ingestion_demo.sh
- 03-agentops-control-tower/scripts/run_summary_demo.sh
- bash -n 03-agentops-control-tower/scripts/*.sh
- git diff --check

Also run from 03-agentops-control-tower:
- uv run pytest
- uv run ruff check .
- uv run mypy src

After implementation, summarize:
1. files created/changed
2. timeline models/functions added
3. summary models/functions added
4. overall health derivation
5. deterministic recommended actions
6. tests added
7. scripts updated/added
8. docs updated
9. prompt history update
10. verification results
11. recommended next milestone
```

## Expected Verification

```bash
03-agentops-control-tower/scripts/run_checks.sh
03-agentops-control-tower/scripts/run_ingestion_demo.sh
03-agentops-control-tower/scripts/run_summary_demo.sh
bash -n 03-agentops-control-tower/scripts/*.sh
git diff --check

cd 03-agentops-control-tower
uv run pytest
uv run ruff check .
uv run mypy src
```

## Result Summary

- Added timeline and summary models to `models.py`.
- Added deterministic timeline generation in `timeline.py`.
- Added deterministic summary generation and combined control tower view
  creation in `summaries.py`.
- Exported summary and timeline APIs from `agentops_control_tower`.
- Added summary/timeline test coverage for events, ordering, counts, health
  status, recommended actions and combined views.
- Added executable local summary demo script.
- Updated `run_checks.sh` to require Milestone 3 files.
- Updated Project 3 docs, root README and portfolio handoff.
- Preserved local-only/read-only scope with no UI, database, scheduler,
  external APIs, secrets or Project 1/Project 2 behavior changes.

## Verification Results

```text
03-agentops-control-tower/scripts/run_checks.sh
PASS - 33 tests passed, ruff clean, mypy clean, git diff --check clean.

03-agentops-control-tower/scripts/run_ingestion_demo.sh
PASS - records=4, warnings=0, errors=0, ok=true.

03-agentops-control-tower/scripts/run_summary_demo.sh
PASS - overall_status=needs_attention, timeline_events=4.

bash -n 03-agentops-control-tower/scripts/*.sh
PASS

git diff --check
PASS

cd 03-agentops-control-tower
uv run pytest
PASS - 33 passed.

uv run ruff check .
PASS

uv run mypy src
PASS - no issues found in 8 source files.
```

## Commit / PR Reference

- Commit: `TBD`
- PR: `TBD`

## Notes

- Local deterministic summary and timeline generation only.
- No dashboard, UI, database, scheduler, external APIs or secrets.
