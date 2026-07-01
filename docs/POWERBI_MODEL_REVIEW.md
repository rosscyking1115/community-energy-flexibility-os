# Power BI model design review

Applying the Power BI model-design-review checklist to the reporting layer
*before* building visuals — the review is a gate, not an afterthought.

## Star-schema compliance

The reporting marts form a **star**, not one flat wide table:

```
        dim_date ─┐
      dim_device ─┼─►  fct_daily_savings   (grain: date x community x household x device)
   dim_community ─┘
```

- **Single fact grain.** `fct_daily_savings` is exactly one row per
  date × community × household × device. The pre-aggregated `rpt_daily_savings`
  and `rpt_monthly_community_savings` are *separate* marts at their own grains
  (day; community-month) — not mixed into the fact.
- **Deliberate decision — ADR:** we did **not** build a single flat
  `RPT_POWERBI_ENERGY_DASHBOARD` wide table (as the original plan sketched).
  A flat table forces one grain, duplicates dimension attributes, and breaks
  cross-filtering. Power BI imports the star and relates on keys instead.

## Relationships

| Check | Design |
|---|---|
| Cardinality | `dim_* (1) → fct_daily_savings (*)` |
| Filter direction | **Single** (dim → fact); no bidirectional filters |
| Join keys | **Integer surrogate keys** (`date_key`, `device_key`, `community_key`), not text |
| FK columns | Hidden from report view in the fact |
| Circular paths | None (single fact) |

Relationship integrity is enforced upstream by dbt `relationships` tests on
every FK — the model can't ship with an orphan key.

## Storage mode

- **Import** is the right default: the data is tiny (~168 rows/2 weeks here;
  ~thousands at community scale) and refreshes daily from the Dagster pipeline.
  Import gives the fastest visuals and full DAX.
- DirectQuery would only be worth it if we needed near-real-time Snowflake reads
  — we don't; the pipeline is daily. Revisit only if a single-household live view
  is added.

## Data quality / governance

- A dedicated **Date dimension** (`dim_date`, marked as a date table) powers the
  time-intelligence measures; no reliance on auto date/time.
- Measures use `DIVIDE` (safe division) and `VAR` — see `powerbi/measures.dax`.
- Row-level security (per community/household) is deferred to Milestone D, where
  it is enforced in the warehouse via Snowflake row-access policies, not just in
  Power BI.

## Pre-launch quick assessment

Run before publishing: confirm one active relationship per dim→fact, all FKs
integer and hidden, `dim_date` marked as the date table, no bidirectional
filters, and every measure using `DIVIDE`/`VAR`.
