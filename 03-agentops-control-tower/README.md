# AgentOps Control Tower

Status: **Static HTML and Markdown report export ready**

AgentOps Control Tower is a local observability and governance layer for AI
automation workflows.

This project is the third portfolio project. It is designed to observe signals
from the earlier projects without duplicating their responsibilities:

- Project 1 produces workflow artifacts such as run history, approval requests
  and generated reports.
- Project 2 provides deterministic local MCP-style tools, CLI evidence,
  guardrails and reviewer checks.
- Project 3 will aggregate and inspect those signals as a local AgentOps
  control tower.

## Planned Focus

Project 3 will focus on:

- workflow run history
- approval states
- failure records
- retry and cadence metadata
- notification status
- LLM and token usage metadata when available
- guardrail outcomes
- local auditability

## Current Milestone

Milestone 5 adds deterministic static HTML report export for a local visual
report artifact.

Project 3 can now parse local evidence into typed records:

- Project 1 run-history JSONL
- Project 1 approval requests JSONL
- Project 1 deterministic Markdown reports
- saved Project 2 CLI JSON evidence
- saved Project 2 guardrail output text

It can also convert ingested records into:

- dashboard-ready summary counts
- a deterministic AgentOps timeline
- an overall local health status
- deterministic local follow-up actions
- compact or pretty JSON for summaries and timelines
- deterministic Markdown reports for stdout or local files
- deterministic static HTML reports for stdout or local files

Missing optional files are reported as warnings. Malformed files are reported as
explicit ingestion errors. Parsed payloads are sanitized with conservative
secret redaction before they are stored in internal records.

## CLI Usage

Run commands from the Project 3 folder with `uv run`:

```bash
uv run agentops-control-tower --help
uv run agentops-control-tower summary --pretty
uv run agentops-control-tower timeline --pretty
uv run agentops-control-tower export-report
uv run agentops-control-tower export-report --format html --output agentops-report.html
```

All commands accept optional local source paths:

```bash
uv run agentops-control-tower summary \
  --run-history ../01-ai-marketing-ops-agent/run-history/workflow-runs.jsonl \
  --approval-requests ../01-ai-marketing-ops-agent/approval-requests/approval-requests.jsonl \
  --report ../01-ai-marketing-ops-agent/reports/daily-marketing-report-demo.md \
  --tool-evidence /path/to/saved-project-2-tool-output.json \
  --guardrail-output /path/to/saved-guardrail-output.txt \
  --pretty
```

Commands:

- `summary`: prints `AgentOpsSummary`-compatible JSON. Compact JSON is the
  default; `--pretty` prints indented JSON.
- `timeline`: prints `AgentOpsTimeline`-compatible JSON. Compact JSON is the
  default; `--pretty` prints indented JSON.
- `export-report`: prints deterministic Markdown to stdout by default.
  `--format html` renders a self-contained static HTML report. `--output PATH`
  writes the report locally and creates parent directories. Existing files are
  not overwritten unless `--overwrite` is passed.

The HTML report is a local file artifact, not a hosted dashboard. It does not
require a web server and does not load external CSS, JavaScript, fonts, images
or CDN assets.

Exit behavior:

- exit `0` when the command succeeds and ingestion has no errors
- exit non-zero when ingestion errors exist, including malformed JSON/JSONL
- exit non-zero for report write conflicts unless `--overwrite` is passed
- warnings alone, including missing optional source files, do not force a
  non-zero exit

Project 3 still does not implement:

- database persistence
- hosted dashboards
- web server
- frontend UI
- frontend framework
- external integrations
- notification providers
- deployed AgentOps services

## Local-First Boundaries

Project 3 is planned as local-first and deterministic. The initial scaffold does
not require secrets, call external APIs, mutate Project 1 artifacts or mutate
Project 2 artifacts.

The Milestone 5 CLI and report export layer remains local-only and read-only
except when writing an explicitly requested local report file. It does not call
LLMs, send notifications, create tasks, load external frontend assets or modify
source artifacts.

## Repository Structure

```text
03-agentops-control-tower/
├── AGENTS.md
├── README.md
├── docs/
├── examples/
├── src/
├── tests/
└── scripts/
```

## Verification

Run the scaffold checks from the repository root:

```bash
03-agentops-control-tower/scripts/run_checks.sh
bash -n 03-agentops-control-tower/scripts/*.sh
git diff --check
```

Run the local ingestion demo:

```bash
03-agentops-control-tower/scripts/run_ingestion_demo.sh
```

Run the local summary demo:

```bash
03-agentops-control-tower/scripts/run_summary_demo.sh
```

Run the local CLI demo:

```bash
03-agentops-control-tower/scripts/run_cli_demo.sh
```

Run the local static HTML report demo:

```bash
03-agentops-control-tower/scripts/run_html_report_demo.sh
```

Run the reviewer-friendly end-to-end demo:

```bash
cd 03-agentops-control-tower
./scripts/run_reviewer_demo.sh
```

The demo scripts generate deterministic temporary evidence with multiple
workflow states, approval states, report states, tool evidence states and
guardrail outcomes. They do not require Project 1 runtime artifacts and do not
mutate Project 1 or Project 2 files. The reviewer demo writes stable generated
artifacts under `exports/reviewer-demo/`, which is ignored by git:

```bash
open exports/reviewer-demo/agentops-report.html
```

## Next Milestone

Project 3 Milestone 6: deepen local AgentOps analysis, such as retry, failure,
approval-state, token or cost summaries when those signals are available.
