# Power BI dashboard guide

How to build `powerbi/community_energy_dashboard.pbix` from the reporting marts.
Everything except the `.pbix` authoring is in the repo: the star-schema marts
(`dbt_energy/models/marts/reporting/`), the DAX (`powerbi/measures.dax`), and the
model review ([POWERBI_MODEL_REVIEW.md](POWERBI_MODEL_REVIEW.md)).

## 0. Get the data (zero-setup path)

Build the marts and export them to CSV (no Snowflake or ODBC driver needed):

```bash
pip install -e ".[warehouse]"
cd dbt_energy && DBT_PROFILES_DIR=. dbt build
python -c "import duckdb; c=duckdb.connect('energy.duckdb'); \
[c.execute(f\"COPY (SELECT * FROM {t}) TO '../powerbi/data/{t}.csv' (HEADER)\") \
for t in ['dim_date','dim_device','dim_community','fct_daily_savings', \
'rpt_daily_savings','rpt_monthly_community_savings']]"
```

This writes six CSVs to `powerbi/data/`. For production, swap this step for a
direct Snowflake `MARTS` connection — the model and measures are identical.

## 1. Connect and model

Import the **four star tables**: `dim_date`, `dim_device`, `dim_community`,
`fct_daily_savings` (Home → Get data → Text/CSV). The two `rpt_*` files are
optional — every page below is built from measures on the star, so you don't
need them in Power BI.

**Relationships** (Model view; each is one-to-many, single filter direction):

| From (one) | To (many) |
|---|---|
| `dim_date[date_key]` | `fct_daily_savings[date_key]` |
| `dim_device[device_key]` | `fct_daily_savings[device_key]` |
| `dim_community[community_key]` | `fct_daily_savings[community_key]` |

Then: mark `dim_date` as the date table (Table tools → Mark as date table →
`full_date`); hide the three `*_key` columns in `fct_daily_savings` from report
view; and add the measures from [`../powerbi/measures.dax`](../powerbi/measures.dax)
(New measure → paste one `Name = …` block at a time).

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
