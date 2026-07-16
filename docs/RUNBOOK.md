# Runbook

How to install, run, operate, and troubleshoot the system. Commands assume the
repo root; on Windows use `set` instead of `export` for env vars.

## Install

```bash
python -m pip install -e ".[dev]"          # core + tests (stdlib-only core)
python -m pip install -e ".[app,reports,warehouse,optim,orchestration,tracking]"  # everything
```

Extras: `app` (Streamlit) · `reports` (Excel/PDF) · `warehouse` (dbt-duckdb) ·
`snowflake` (dbt-snowflake) · `optim` (PuLP LP optimiser) · `orchestration`
(Dagster) · `tracking` (MLflow).

## Run the pieces

| Task | Command |
|---|---|
| Tests | `python -m pytest` |
| One optimisation (CLI) | `python -m community_energy_flex cheapest` (or balanced / lowest_carbon / avoid_peak) |
| Decision app | `streamlit run app/streamlit_app.py` |
| Build the warehouse (DuckDB) | `cd dbt_energy && DBT_PROFILES_DIR=. dbt build` |
| Build on Snowflake | `dbt build --target snowflake` (see [SNOWFLAKE_SETUP.md](SNOWFLAKE_SETUP.md)) |
| Daily pipeline (Dagster UI) | `dagster dev -m orchestration.definitions` |
| Optimiser comparison → MLflow | `python -m community_energy_flex.experiments.optimiser_comparison` then `mlflow ui` |
| Power BI data | rebuild + export CSVs ([POWERBI_DASHBOARD_GUIDE.md](POWERBI_DASHBOARD_GUIDE.md) step 0) |

## Daily operational flow

The pipeline (`community_energy_flex.pipeline.daily`, wrapped by Dagster) runs
once a day, early:

```
fetch carbon forecast → validate → optimise → record monitoring → write reports
```

Every run writes to the monitoring store (CSV locally, `MONITORING.*` on
Snowflake): `pipeline_runs`, `optimisation_quality`, `data_freshness`. The
schedule is `daily_optimisation_run` at 05:30 Europe/London.

## Failure handling

The pipeline degrades gracefully — it never leaves users with nothing:

| Symptom | Behaviour / action |
|---|---|
| Carbon API unreachable | Falls back to the **last good schedule** (`status="fallback"`), logs it. |
| Forecast missing for tomorrow (< 48 slots) | `DataValidationError`; run recorded `failed`; last good served if available. |
| No last good schedule yet | `status="failed"`, no schedule; investigate the fetch/source. |
| Tariff entered wrong | Optimiser still runs; robustness drops for manual tariffs and the caveat says so. |
| Optimiser infeasible (LP, tight peak cap) | `InfeasibleScheduleError` — relax `max_load_kw` or the task deadlines. |
| Stale data | `dbt source freshness` warns > 6 h / errors > 12 h on the carbon RAW table. |

Check recent runs: read `monitoring_data/pipeline_runs.csv` (or query
`MONITORING.PIPELINE_RUNS`).

## Auth / access control

- **Local/demo:** no setup — the app has a role picker.
- **Production:** configure OIDC in `.streamlit/secrets.toml` (`[auth]` block) and
  apply `warehouse/row_access_policies.sql`, populating `APP.USER_ACCESS`. Full
  steps: [RBAC_MODEL.md](RBAC_MODEL.md).

## Verify a change

`python -m pytest` (unit + optimiser invariants + auth + a headless Streamlit
AppTest) and `ruff check .`. CI runs both on 3.11–3.13. The Streamlit app can be
smoke-tested headlessly with `streamlit.testing.v1.AppTest` — no browser needed.

## Reproduce the case study

`PYTHONPATH=src python scripts/case_study.py` — the numbers in
[CASE_STUDY.md](CASE_STUDY.md) come straight from this.
