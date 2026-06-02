# Marketing Report Skill

Use this skill when generating or reviewing daily marketing operations reports.

## Purpose

Create concise, evidence-backed Markdown reports for marketing stakeholders from
validated campaign data, anomaly findings, recommendations and workflow logs.

## Inputs

- `CampaignSnapshot` objects from the deterministic aggregation layer.
- `AnomalyFinding` objects from deterministic anomaly detection.
- Optional `LLMInterpretationResult` from the LLM interpretation layer.
- Optional `ApprovalRequest` and `ApprovalDecision` records from the approval
  layer.
- Optional `NotificationResult` records from approval-aware notification
  delivery.
- Optional report metadata such as title and generated timestamp.
- Human approval records must remain separate from deterministic facts and LLM
  recommendations.

Do not generate reports from raw scraped rows, raw REST responses or raw GraphQL
responses.

## Output Expectations

- Start with the report title and generated timestamp.
- Include an executive summary.
- Include campaign health overview, critical anomalies, warning anomalies, data
  quality issues, human review required, campaign snapshot table, deterministic
  recommended actions and limitations / missing data.
- List critical findings before warnings and warnings before info.
- Sort campaigns by campaign ID unless a workflow documents another stable
  deterministic ordering.
- Include campaign IDs and metric values for traceability.
- Separate deterministic findings from LLM interpretation.
- Keep LLM facts and recommendations in their own section when included.
- Keep pending, approved and rejected approval requests in their own section
  when included.
- Keep notification delivery status separate from deterministic report facts.
- Render unavailable values as missing; avoid inventing missing data.
- End with concrete next actions and ownership.

## Safety Rules

- Do not include secrets, credentials or private customer data.
- Flag missing, stale or low-confidence data explicitly.
- Preserve data quality flags exactly; do not downgrade or remove them.
- Never invent missing metrics, causes, trends or campaign data.
- Do not recommend budget changes without a human approval checkpoint.
- Treat `requires_human_review` as blocking sensitive automated action.
- Treat pending approval requests as blocking notification or external action.
- Never describe pending approval requests as approved actions in notification
  summaries.
- Keep source data references so the report can be audited.
- Keep deterministic recommendations conservative and based on known finding
  types.
- Use LLM output only for interpretation, summarization and recommendations;
  never use it to overwrite deterministic findings.
