# Data Sources

Project 3 will consume local evidence from Project 1 and Project 2.

Milestone 2 adds deterministic local parsers for selected source files. The
parsers read local files only and return typed records, warnings and errors.

## Project 1 Sources

Supported local inputs:

- `01-ai-marketing-ops-agent/run-history/*.jsonl`
- `01-ai-marketing-ops-agent/approval-requests/*.jsonl`
- `01-ai-marketing-ops-agent/reports/*.md`

These files represent workflow run history, approval states and generated
business reports.

## Project 2 Sources

Supported local inputs:

- Project 2 MCP-style tool outputs.
- `agent-toolkit-mcp` CLI output.
- local CI mirror results.
- guardrail script output.
- prompt-history records.

These files and command outputs represent local review evidence, safety checks
and deterministic tool-layer observations. Project 3 parses saved evidence only;
it does not invoke Project 2 tools as part of ingestion.

## Ingestion Behavior

- Missing optional files return warnings.
- Malformed JSON and JSONL files return explicit ingestion errors.
- Markdown reports are parsed only for supported deterministic summary fields.
- Guardrail output status is classified only when text contains simple pass,
  fail or block signals.
- Secret-like keys and values are conservatively redacted.

## CLI Source Options

Milestone 4 exposes the supported local inputs through the
`agentops-control-tower` CLI:

- `--run-history PATH`
- `--approval-requests PATH`
- `--report PATH`
- `--tool-evidence PATH`
- `--guardrail-output PATH`

These options map directly to the same local source parameters accepted by
`ingest_local_agentops_sources`. Project 3 reads saved local evidence only; it
does not invoke Project 1 workflows or Project 2 tools during CLI ingestion.

`agentops-control-tower export-report` can render the same ingested local
sources as Markdown or static HTML with `--format markdown|html`. The format
option changes only the local export representation, not the source ingestion
behavior.

## Source Boundaries

Project 3 should read local files and command outputs only unless a future
milestone explicitly introduces another source. The scaffold does not call
external APIs, require secrets or mutate source artifacts.
