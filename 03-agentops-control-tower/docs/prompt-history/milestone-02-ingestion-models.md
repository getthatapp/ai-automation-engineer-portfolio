# Project 3 Milestone 2 - Local Data Ingestion Models

Status: `Complete`
Branch: `feature/project-3-m02-ingestion-models`

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
- 03-agentops-control-tower/docs/prompt-history/milestone-01-scaffold.md

Continue Project 3: 03-agentops-control-tower.

Milestone 2: local data ingestion models.

Branch:
feature/project-3-m02-ingestion-models

Prompt history requirement:
Create or update:
03-agentops-control-tower/docs/prompt-history/milestone-02-ingestion-models.md

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
- Project 3 is a local AgentOps / workflow observability control tower.
- Project 3 does not yet implement ingestion, models, dashboards, backend services or UI.
- This milestone should add only local deterministic ingestion models and parsers.
- Do not modify Project 1 code.
- Do not modify Project 2 code unless only documentation links require it.
- Do not change Project 1 or Project 2 runtime behavior.
- Do not add frontend UI.
- Do not add external integrations.
- Do not call external APIs.
- Do not require secrets.

Goal:
Implement the first local deterministic ingestion layer for Project 3.

The ingestion layer should parse local artifacts from Project 1 and Project 2 into typed internal models for future observability dashboards and summaries.

Implement:

1. Add Python project structure under:
   03-agentops-control-tower/

Suggested files:
- pyproject.toml
- src/agentops_control_tower/__init__.py
- src/agentops_control_tower/models.py
- src/agentops_control_tower/ingestion.py
- src/agentops_control_tower/parsers.py
- src/agentops_control_tower/errors.py
- src/agentops_control_tower/sanitization.py
- tests/

2. Use Python 3.12+.

3. Use Pydantic models if practical and consistent with the rest of the portfolio.
If Pydantic is added, keep dependency minimal and explicit.

4. Add typed models for local observability records.

Suggested models:
- WorkflowRunRecord
- ApprovalRequestRecord
- ReportSummaryRecord
- ToolEvidenceRecord
- GuardrailEvidenceRecord
- IngestionResult
- IngestionWarning
- IngestionSourceType enum
- WorkflowStatus enum if useful
- ApprovalStatus enum if useful

5. Implement local parsers:

parse_run_history_jsonl(path, limit=None):
- Parses Project 1 workflow run-history JSONL.
- Handles missing file safely.
- Handles malformed JSONL explicitly.
- Preserves deterministic ordering.
- Redacts secret-like values.
- Returns typed IngestionResult.

parse_approval_requests_jsonl(path, status_filter=None):
- Parses Project 1 approval request JSONL.
- Supports optional status filter for pending/approved/rejected if represented in source data.
- Handles missing file safely.
- Handles malformed JSONL explicitly.
- Redacts secret-like values.
- Returns typed IngestionResult.

parse_markdown_report(path):
- Parses Project 1 deterministic Markdown report.
- Extracts at least:
  - generated timestamp if present,
  - campaigns processed if present,
  - critical findings if present,
  - warning findings if present,
  - campaigns requiring human review if present,
  - whether required report sections are present.
- Does not infer missing metrics.
- Does not call LLM.
- Returns typed IngestionResult.

parse_tool_evidence_json(path):
- Parses Project 2 CLI JSON evidence if saved to a local file.
- Handles missing file safely.
- Handles malformed JSON explicitly.
- Redacts secret-like values.
- Returns typed IngestionResult.

parse_guardrail_output_text(path):
- Parses saved Project 2 guardrail output text if present.
- Extracts simple status signals such as passed/failed/blocked if possible.
- Does not infer more than text supports.
- Returns typed IngestionResult.

6. Add aggregator function:

ingest_local_agentops_sources(...)
- Accepts optional paths for:
  - run history JSONL
  - approval requests JSONL
  - Markdown report
  - Project 2 tool evidence JSON
  - Project 2 guardrail output text
- Calls relevant parsers for provided paths only.
- Returns a combined typed result.
- Must not mutate files.
- Must not call external services.

7. Sanitization:
- Add conservative secret redaction for keys and values.
- Do not print secret values in errors.
- Add tests proving obvious secret-like values are redacted.

8. Error handling:
- Add clear custom errors if useful.
- Missing optional files should produce warnings, not crashes.
- Malformed files should produce explicit errors inside the ingestion result unless the parser should raise. Prefer typed result errors over unhandled exceptions for user-facing ingestion.

9. Tests:
Add tests for:
- run history happy path
- run history missing file
- run history malformed JSONL
- run history secret redaction
- approval requests happy path
- approval requests status filtering
- approval requests missing file
- report parsing happy path
- report missing section warnings
- report missing file
- tool evidence JSON happy path
- tool evidence malformed JSON
- guardrail output pass/fail/block extraction
- combined ingestion with multiple sources
- deterministic ordering

10. Scripts:
Update or add:
- 03-agentops-control-tower/scripts/run_checks.sh

It should now:
- verify scaffold files exist
- run bash syntax checks
- run Python tests
- run ruff if configured
- run mypy if configured
- run git diff --check if practical or document that this is run from root

Add optional:
- 03-agentops-control-tower/scripts/run_ingestion_demo.sh

Behavior:
- local-only
- read-only
- use sample temporary files or existing safe paths if available
- print a short deterministic ingestion summary
- no external APIs
- no secrets

11. Documentation updates:
- 03-agentops-control-tower/README.md
- 03-agentops-control-tower/docs/ARCHITECTURE.md
- 03-agentops-control-tower/docs/ROADMAP.md
- 03-agentops-control-tower/docs/OBSERVABILITY_MODEL.md
- 03-agentops-control-tower/docs/DATA_SOURCES.md
- 03-agentops-control-tower/docs/SAFETY_MODEL.md
- 03-agentops-control-tower/docs/LOCAL_DEMO_PLAN.md
- docs/CODEX_HANDOFF_AI_AUTOMATION_PORTFOLIO.md
- root README.md only if useful and concise

12. Documentation should explain:
- what local sources can now be parsed
- what models exist
- what is not implemented yet
- that ingestion is local-only and deterministic
- that missing optional files are warnings
- that malformed files are explicit ingestion errors
- that no dashboard/UI exists yet
- that this milestone prepares Project 3 for later summaries and dashboard work

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
- Do not overclaim a dashboard, database, scheduler or deployed AgentOps platform.
- Keep scripts executable.
- Add Google-style docstrings to every new or modified Python function, method and class.
- Keep prompt history current.
- Keep tests deterministic.
- Avoid broad refactors unrelated to this milestone.

Expected verification:
Run:
- 03-agentops-control-tower/scripts/run_checks.sh
- bash -n 03-agentops-control-tower/scripts/*.sh
- git diff --check

If Python package checks are configured separately, also run from 03-agentops-control-tower:
- uv run pytest
- uv run ruff check .
- uv run mypy src

After implementation, summarize:
1. files created/changed
2. ingestion models added
3. parsers added
4. sanitization behavior
5. tests added
6. scripts updated/added
7. docs updated
8. prompt history update
9. verification results
10. recommended next milestone
```

## Expected Verification

```bash
03-agentops-control-tower/scripts/run_checks.sh
bash -n 03-agentops-control-tower/scripts/*.sh
git diff --check

cd 03-agentops-control-tower
uv run pytest
uv run ruff check .
uv run mypy src
```

## Result Summary

- Added Python package structure under `src/agentops_control_tower/`.
- Added Pydantic ingestion models for workflow runs, approval requests, report
  summaries, tool evidence, guardrail evidence, warnings and errors.
- Added deterministic local parsers for Project 1 run-history JSONL, approval
  request JSONL and Markdown reports.
- Added deterministic local parsers for saved Project 2 CLI JSON evidence and
  guardrail output text.
- Added combined local ingestion entry point.
- Added conservative recursive redaction for secret-like keys and values.
- Added deterministic parser and sanitization tests.
- Updated Project 3 checks to run tests, ruff, mypy and `git diff --check`.
- Added local temporary-file ingestion demo script.
- Updated Project 3 docs, root README and portfolio handoff.
- Preserved local-only/read-only boundaries and did not modify Project 1 or
  Project 2 behavior.

## Verification Results

```text
03-agentops-control-tower/scripts/run_checks.sh
PASS - 16 tests passed, ruff clean, mypy clean, git diff --check clean.

bash -n 03-agentops-control-tower/scripts/*.sh
PASS

git diff --check
PASS

cd 03-agentops-control-tower
uv run pytest
PASS - 16 passed.

uv run ruff check .
PASS

uv run mypy src
PASS - no issues found in 6 source files.

03-agentops-control-tower/scripts/run_ingestion_demo.sh
PASS - records=4, warnings=0, errors=0, ok=true.
```

## Commit / PR Reference

- Commit: `TBD`
- PR: `TBD`

## Notes

- Local deterministic ingestion only.
- No dashboard, UI, database, scheduler, external APIs or secrets.
