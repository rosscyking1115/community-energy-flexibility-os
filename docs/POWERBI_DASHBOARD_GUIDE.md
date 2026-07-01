# Power BI dashboard guide

How to build `powerbi/community_energy_dashboard.pbix` from the reporting marts.
Everything except the `.pbix` authoring is in the repo: the star-schema marts
(`dbt_energy/models/marts/reporting/`), the DAX (`powerbi/measures.dax`), and the
model review ([POWERBI_MODEL_REVIEW.md](POWERBI_MODEL_REVIEW.md)).

## 1. Connect

Point Power BI at Snowflake `MARTS` (or the DuckDB dev build) and import:

- `fct_daily_savings`, `dim_date`, `dim_device`, `dim_community` (the star)
- `rpt_daily_savings`, `rpt_monthly_community_savings` (pre-aggregated pages)

Set relationships dim→fact (single direction, integer keys), mark `dim_date` as
the date table, hide the FK columns, then paste in the measures from
`measures.dax`.

## 2. Pages

**Page 1 — Executive Summary.** Cards: `Total Cost Saving (GBP)`,
`Total Carbon Saving (kg)`, `Peak Slots Avoided`, `Tasks Optimised`,
`Avg Recommendation Confidence`.

**Page 2 — Cost & Carbon Timeline.** Line chart of `rpt_daily_savings` over
`dim_date[full_date]`; `Cost Saving (GBP) MoM %` KPI; baseline-vs-optimised
columns.

**Page 3 — Device Contribution.** Bar of `Total Cost Saving` by
`dim_device[device_type]`; `Peak Slots Avoided` by device.

**Page 4 — Community Comparison.** `rpt_monthly_community_savings` by
`dim_community[community_name]`; `Households Participating`; average savings.

**Page 5 — Recommendation Quality.** `Avg Recommendation Confidence` distribution;
`Trusted Cost Saving (GBP)` vs total (shows how much saving is high-confidence);
data-freshness and constraint-violation indicators from `MONITORING.*`.

## 3. Publish

Export a PDF and screenshots into `powerbi/screenshots/` for the README and the
case study. Keep the safety caveat visible: planning advice only, no guaranteed
savings.
