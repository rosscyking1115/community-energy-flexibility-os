# Community Energy Flexibility OS

> Decision-support that tells households and small organisations **when** to run
> flexible electricity loads to cut cost and carbon — while respecting their
> comfort constraints.

[![CI](https://github.com/rosscyking1115/community-energy-flexibility-os/actions/workflows/ci.yml/badge.svg)](https://github.com/rosscyking1115/community-energy-flexibility-os/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-informational.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](pyproject.toml)

It doesn't just show *"carbon is low at 02:00."* It says *"run the washing machine
02:30–04:00, charge the EV 01:30–04:30, expected saving £0.12 and 0.14 kg CO₂,
high confidence"* — with the assumptions and caveats attached.

> [!TIP]
> **Worked example:** Riverside Community Centre — four flexible loads, no
> batteries, no solar, no smart meter — saves **~£149 and ~179 kg CO₂ a year**
> just by shifting *when* things run. And when the grid came in ~8% dirtier than
> forecast, the plan still realised **108% of its forecast carbon saving**. Read
> the full worked example → [docs/CASE_STUDY.md](docs/CASE_STUDY.md).

> [!NOTE]
> Planning advice only. This tool does not control appliances, guarantee savings,
> or replace official energy or supplier advice.

## Live

The engine runs behind a public, keyless API (FastAPI on Fly.io):

**`https://community-energy-flex-api.fly.dev`** — [OpenAPI docs](https://community-energy-flex-api.fly.dev/docs)

```bash
# tonight's cleanest/cheapest window for a load in London, from live data
curl -s https://community-energy-flex-api.fly.dev/v1/optimise \
  -H 'content-type: application/json' \
  -d '{"region_id":"london","tariff":{"kind":"agile"},"objective":"balanced",
       "tasks":[{"name":"Washing machine","device_type":"Washing machine",
       "energy_kwh":0.8,"duration_hours":1.5,"earliest":"00:00","latest":"08:00",
       "preferred":"06:30"}]}'
```

Endpoints: `/v1/regions`, `/v1/appliances`, `/v1/tariffs/agile/{region}`,
`/v1/forecast/{region}` (the 48-slot carbon + price curve), `/v1/optimise`. Data
is live: GB regional carbon (NESO / National Grid Carbon Intensity) and Octopus
Agile prices, with an EirGrid typical-day profile for Northern Ireland.

The consumer website that consumes it — **"After Midnight"**, a Next.js planner
built around a full-day carbon/price band — lives in [`web/`](web); see
[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) to run or deploy it.

## What's inside

An end-to-end, open-source reference build for community energy planning:

- **Optimiser** — rule-based (cheapest / greenest / balanced / avoid-peak) plus an
  LP/MILP optimiser (PuLP) that schedules loads jointly under a peak-load cap. Every
  recommendation carries a baseline comparison, a confidence band, and a caveat.
- **Public API + website** — a FastAPI service wrapping the engine (live on Fly.io)
  and a Next.js consumer app wired to it through a server-side BFF.
- **Data** — GB Carbon Intensity API; tariff models (flat / Economy 7 / time-of-use /
  Octopus Agile); Open-Meteo weather.
- **Warehouse** — dbt on DuckDB (dev) with a Snowflake target, plus a reporting star.
- **Orchestration** — a Dagster daily pipeline with keep-last-good-schedule fallback
  and a **forecast-vs-actual retro loop** ("did yesterday's plan actually save?").
- **Apps & reports** — a Streamlit decision app, a Power BI stakeholder dashboard,
  and text / Excel / PDF action reports.
- **Access control** — role-based scoping + an audit trail, enforced in the app and
  (defence in depth) by Snowflake row-access policies.
- **Tracking** — an MLflow comparison of optimiser strategies.

## Quickstart

```bash
python -m pip install -e ".[dev]"          # stdlib-only core + tests
python -m pytest                            # full suite
python -m community_energy_flex cheapest    # end-to-end on sample data
```

Run the decision app:

```bash
python -m pip install -e ".[app,reports]"
streamlit run app/streamlit_app.py
```

Run the public API locally:

```bash
python -m pip install -e ".[api]"
python -m uvicorn community_energy_api.main:app --app-dir api --port 8000
```

Everything else — warehouse, pipeline, LP optimiser, MLflow, Power BI data — is an
optional extra. See [docs/RUNBOOK.md](docs/RUNBOOK.md) to run each piece.

## How it works

```
Carbon Intensity API ─┐
Tariff (flat/E7/ToU) ─┼─► half-hourly "energy options" ─► optimiser ───────────► schedule
Your task constraints ┘        (dbt / DuckDB)             rule-based + LP/MILP     + baseline
                                                          (peak-load aware)        + savings
                                                                                   + confidence
                                                                                      │
                                    Public API + web ◄──┬── Streamlit app · Excel/PDF report ◄──┘
                                    (FastAPI + Next.js)  └── Power BI dashboard  (Snowflake star)
```

The day is 48 half-hour **slots**. Tasks, tariffs, and carbon forecasts are all
expressed in slots, so the optimiser reasons over one clean integer axis. Every
recommendation is compared against a **baseline** (business as usual) and carries a
**confidence** band and a plain-language **caveat**. The maths behind those three is
spelled out in [docs/METHODOLOGY.md](docs/METHODOLOGY.md).

## Project layout

| Path | What's there |
|---|---|
| `src/community_energy_flex/` | Core engine: `domain/`, `data_sources/`, `optimisation/`, `reporting/`, `pipeline/`, `monitoring/`, `auth/`, `experiments/` |
| `api/` | Public FastAPI service (`community_energy_api`) — regions, appliances, live carbon/Agile forecast, optimise |
| `web/` | Next.js website "After Midnight" — the consumer planner, wired to the API |
| `app/streamlit_app.py` | The Streamlit decision app (power-user / ops tool) |
| `orchestration/` | Dagster assets/jobs/schedules (thin wrappers over `pipeline/`) |
| `dbt_energy/` | dbt warehouse (DuckDB dev + Snowflake target), staging → options mart + reporting star |
| `warehouse/` | Snowflake bootstrap DDL + row-access policies |
| `powerbi/` | Dashboard `.pbix`, DAX measures, theme |
| `tests/` · `api/tests/` | Optimiser invariants, confidence, tariffs, reports, auth, API |
| `docs/` | See the index below |

### Docs

| Doc | What |
|---|---|
| [PRODUCT_THESIS](docs/PRODUCT_THESIS.md) · [ROADMAP](docs/ROADMAP.md) | Why it exists; the build plan |
| [CASE_STUDY](docs/CASE_STUDY.md) | Worked community-centre example (start here) |
| [METHODOLOGY](docs/METHODOLOGY.md) | Baseline, cost/carbon maths, confidence |
| [ARCHITECTURE](docs/ARCHITECTURE.md) | Layers, deep-module review, ADRs |
| [DEPLOYMENT](docs/DEPLOYMENT.md) | API on Fly.io + web on Vercel |
| [DATA_SOURCES](docs/DATA_SOURCES.md) · [SAFETY_AND_PRIVACY](docs/SAFETY_AND_PRIVACY.md) | Inputs & licensing; safety, privacy, RBAC scope |
| [SNOWFLAKE_SETUP](docs/SNOWFLAKE_SETUP.md) · [DAGSTER_PIPELINE](docs/DAGSTER_PIPELINE.md) | Warehouse & orchestration |
| [POWERBI_DASHBOARD_GUIDE](docs/POWERBI_DASHBOARD_GUIDE.md) · [POWERBI_MODEL_REVIEW](docs/POWERBI_MODEL_REVIEW.md) · [POWERBI_COPILOT_HANDOFF](docs/POWERBI_COPILOT_HANDOFF.md) | Build, review, and polish the dashboard |
| [RBAC_MODEL](docs/RBAC_MODEL.md) | Roles, two-layer enforcement, OIDC |
| [RUNBOOK](docs/RUNBOOK.md) | Operate it; failure handling |

## Data sources

- **GB Carbon Intensity API** (carbonintensity.org.uk) — free, no key.
- **Octopus Agile** — live half-hourly unit rates by region (GSP group).
- **EirGrid** — a typical-day carbon profile for Northern Ireland (no live GB feed).
- **Weather** — Open-Meteo (free, no key), for the demand/solar features.

See [docs/DATA_SOURCES.md](docs/DATA_SOURCES.md) for fields and licensing.

## Status

| Piece | State |
|---|---|
| Engine, warehouse, Streamlit app, Power BI, RBAC | Done (v0.1.0) |
| Public API (FastAPI) | **Live** on Fly.io |
| Website ("After Midnight", Next.js) | Built; Vercel deploy pending |
| Next | Wide-data / explainability pass, then growth (region pages, PWA) |

## Contributing & licence

Contributions welcome — see [CONTRIBUTING.md](CONTRIBUTING.md). MIT [LICENSE](LICENSE).
