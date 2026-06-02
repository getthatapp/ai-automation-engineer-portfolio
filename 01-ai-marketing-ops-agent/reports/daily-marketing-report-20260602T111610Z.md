# Daily Marketing Operations Report

Generated timestamp: 2026-06-02T11:16:10.818053+00:00

## Executive Summary
- Campaigns processed: 3.
- Healthy campaigns: 0.
- Critical findings: 3.
- Warning findings: 3.
- Informational findings: 0.
- Campaigns requiring human review: 3.

## Campaign Health Overview
| Campaign ID | Status | Critical | Warning | Info | Human Review |
| --- | --- | --- | --- | --- | --- |
| cmp-email-winback | human_review_required | 1 | 1 | 0 | yes |
| cmp-search-brand | human_review_required | 1 | 1 | 0 | yes |
| cmp-social-retargeting | human_review_required | 1 | 1 | 0 | yes |

## Critical Anomalies
- `cmp-email-winback` requires_human_review (source: `aggregation_data_quality`, human review: yes): Snapshot requires human review before automated follow-up actions. Evidence: analytics_campaign_id=cmp-email-winback; analytics_conversions=410; analytics_cost=1200.00; analytics_revenue=18900.00; campaign_api_campaign_id=cmp-email-winback; campaign_api_collected_at=2026-05-28T08:00:00+00:00; campaign_api_conversions=410; campaign_api_revenue=18900.00; campaign_api_spend=1200.00; data_quality_flag=requires_human_review; data_quality_flags=stale_data,requires_human_review; data_quality_notes=Campaign REST API metadata is older than 24 hours. | Snapshot requires human review before automated follow-up actions.; panel_campaign_id=cmp-email-winback; panel_conversions=410; panel_cpa=2.93; panel_revenue=18900.00; panel_roi=14.75; panel_spend=1200.00.
- `cmp-search-brand` requires_human_review (source: `aggregation_data_quality`, human review: yes): Snapshot requires human review before automated follow-up actions. Evidence: analytics_campaign_id=cmp-search-brand; analytics_conversions=640; analytics_cost=12150.00; analytics_revenue=38400.00; campaign_api_campaign_id=cmp-search-brand; campaign_api_collected_at=2026-05-28T08:00:00+00:00; campaign_api_conversions=640; campaign_api_revenue=38400.00; campaign_api_spend=12150.00; data_quality_flag=requires_human_review; data_quality_flags=stale_data,requires_human_review; data_quality_notes=Campaign REST API metadata is older than 24 hours. | Snapshot requires human review before automated follow-up actions.; panel_campaign_id=cmp-search-brand; panel_conversions=640; panel_cpa=18.98; panel_revenue=38400.00; panel_roi=2.16; panel_spend=12150.00.
- `cmp-social-retargeting` requires_human_review (source: `aggregation_data_quality`, human review: yes): Snapshot requires human review before automated follow-up actions. Evidence: analytics_campaign_id=cmp-social-retargeting; analytics_conversions=310; analytics_cost=9800.00; analytics_revenue=21700.00; campaign_api_campaign_id=cmp-social-retargeting; campaign_api_collected_at=2026-05-28T08:00:00+00:00; campaign_api_conversions=310; campaign_api_revenue=21700.00; campaign_api_spend=9800.00; data_quality_flag=requires_human_review; data_quality_flags=stale_data,requires_human_review; data_quality_notes=Campaign REST API metadata is older than 24 hours. | Snapshot requires human review before automated follow-up actions.; panel_campaign_id=cmp-social-retargeting; panel_conversions=310; panel_cpa=31.61; panel_revenue=21700.00; panel_roi=1.21; panel_spend=9800.00.

## Warning Anomalies
- `cmp-email-winback` stale_data (source: `aggregation_data_quality`, human review: no): Campaign metadata is stale. Evidence: analytics_campaign_id=cmp-email-winback; analytics_conversions=410; analytics_cost=1200.00; analytics_revenue=18900.00; campaign_api_campaign_id=cmp-email-winback; campaign_api_collected_at=2026-05-28T08:00:00+00:00; campaign_api_conversions=410; campaign_api_revenue=18900.00; campaign_api_spend=1200.00; data_quality_flag=stale_data; data_quality_flags=stale_data,requires_human_review; data_quality_notes=Campaign REST API metadata is older than 24 hours. | Snapshot requires human review before automated follow-up actions.; panel_campaign_id=cmp-email-winback; panel_conversions=410; panel_cpa=2.93; panel_revenue=18900.00; panel_roi=14.75; panel_spend=1200.00.
- `cmp-search-brand` stale_data (source: `aggregation_data_quality`, human review: no): Campaign metadata is stale. Evidence: analytics_campaign_id=cmp-search-brand; analytics_conversions=640; analytics_cost=12150.00; analytics_revenue=38400.00; campaign_api_campaign_id=cmp-search-brand; campaign_api_collected_at=2026-05-28T08:00:00+00:00; campaign_api_conversions=640; campaign_api_revenue=38400.00; campaign_api_spend=12150.00; data_quality_flag=stale_data; data_quality_flags=stale_data,requires_human_review; data_quality_notes=Campaign REST API metadata is older than 24 hours. | Snapshot requires human review before automated follow-up actions.; panel_campaign_id=cmp-search-brand; panel_conversions=640; panel_cpa=18.98; panel_revenue=38400.00; panel_roi=2.16; panel_spend=12150.00.
- `cmp-social-retargeting` stale_data (source: `aggregation_data_quality`, human review: no): Campaign metadata is stale. Evidence: analytics_campaign_id=cmp-social-retargeting; analytics_conversions=310; analytics_cost=9800.00; analytics_revenue=21700.00; campaign_api_campaign_id=cmp-social-retargeting; campaign_api_collected_at=2026-05-28T08:00:00+00:00; campaign_api_conversions=310; campaign_api_revenue=21700.00; campaign_api_spend=9800.00; data_quality_flag=stale_data; data_quality_flags=stale_data,requires_human_review; data_quality_notes=Campaign REST API metadata is older than 24 hours. | Snapshot requires human review before automated follow-up actions.; panel_campaign_id=cmp-social-retargeting; panel_conversions=310; panel_cpa=31.61; panel_revenue=21700.00; panel_roi=1.21; panel_spend=9800.00.

## Data Quality Issues
- `cmp-email-winback`: flags=stale_data, requires_human_review; notes=Campaign REST API metadata is older than 24 hours. | Snapshot requires human review before automated follow-up actions.; related findings: critical requires_human_review, warning stale_data; human review: yes.
- `cmp-search-brand`: flags=stale_data, requires_human_review; notes=Campaign REST API metadata is older than 24 hours. | Snapshot requires human review before automated follow-up actions.; related findings: critical requires_human_review, warning stale_data; human review: yes.
- `cmp-social-retargeting`: flags=stale_data, requires_human_review; notes=Campaign REST API metadata is older than 24 hours. | Snapshot requires human review before automated follow-up actions.; related findings: critical requires_human_review, warning stale_data; human review: yes.

## Human Review Required
- `cmp-email-winback`: snapshot requires human review; requires_human_review.
- `cmp-search-brand`: snapshot requires human review; requires_human_review.
- `cmp-social-retargeting`: snapshot requires human review; requires_human_review.

## Campaign Snapshot Table
| Campaign ID | Name | Channel | Panel Spend | Panel Conversions | Panel Revenue | Campaign API Spend | Analytics Cost | Quality Flags | Human Review |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| cmp-email-winback | Email Winback | email | 1200.00 | 410 | 18900.00 | 1200.00 | 1200.00 | stale_data, requires_human_review | yes |
| cmp-search-brand | Brand Search Defense | search | 12150.00 | 640 | 38400.00 | 12150.00 | 12150.00 | stale_data, requires_human_review | yes |
| cmp-social-retargeting | Retargeting Social | social | 9800.00 | 310 | 21700.00 | 9800.00 | 9800.00 | stale_data, requires_human_review | yes |

## Deterministic Recommended Actions
- `cmp-email-winback`: pause automated follow-up until a human reviews the cited evidence.
- `cmp-search-brand`: pause automated follow-up until a human reviews the cited evidence.
- `cmp-social-retargeting`: pause automated follow-up until a human reviews the cited evidence.
- `cmp-email-winback`: refresh campaign metadata before downstream reporting or action.
- `cmp-search-brand`: refresh campaign metadata before downstream reporting or action.
- `cmp-social-retargeting`: refresh campaign metadata before downstream reporting or action.

## Limitations / Missing Data
- Report content is limited to CampaignSnapshot and AnomalyFinding inputs; raw scraped rows, raw REST responses and raw GraphQL responses are not consumed.
- LLM interpretation is not included in this deterministic report.
- Unavailable metrics are shown as `missing` and are not inferred.
- Missing campaign metadata: none.
- Missing analytics metrics: none.
