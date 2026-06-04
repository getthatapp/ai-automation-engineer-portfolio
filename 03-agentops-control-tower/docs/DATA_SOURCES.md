# Data Sources

Project 3 will consume local evidence from Project 1 and Project 2.

The current scaffold documents the intended sources only. It does not yet parse
or ingest them.

## Project 1 Sources

Planned local inputs:

- `01-ai-marketing-ops-agent/run-history/*.jsonl`
- `01-ai-marketing-ops-agent/approval-requests/*.jsonl`
- `01-ai-marketing-ops-agent/reports/*.md`

These files represent workflow run history, approval states and generated
business reports.

## Project 2 Sources

Planned local inputs:

- Project 2 MCP-style tool outputs.
- `agent-toolkit-mcp` CLI output.
- local CI mirror results.
- guardrail script output.
- prompt-history records.

These files and command outputs represent local review evidence, safety checks
and deterministic tool-layer observations.

## Source Boundaries

Project 3 should read local files and command outputs only unless a future
milestone explicitly introduces another source. The scaffold does not call
external APIs, require secrets or mutate source artifacts.
