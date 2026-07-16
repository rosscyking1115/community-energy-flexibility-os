# Project status

**Release:** v0.2.0 credibility closeout  
**State:** feature frozen  
**Product and repository name:** Community Energy Flex

Community Energy Flex is a portfolio decision-support demonstrator for scheduling flexible electricity demand. It is not connected to customer meters or appliances and does not claim measured operational savings.

## Capability status matrix

| Capability | Status | Evidence / boundary |
|---|---|---|
| Rule-based scheduling | running | Core optimiser and invariant tests |
| LP/MILP scheduling | built-local | Optional PuLP path and parity/invariant tests |
| Next.js web client | running | Public Vercel deployment; dated reachability recorded in the release evidence |
| FastAPI service | running | Public Fly.io deployment; health, OpenAPI, forecast, and optimise smoke recorded at release |
| GB Carbon Intensity forecast | running with fallback | Response provenance distinguishes live forecast from labelled GB sample fallback |
| Northern Ireland carbon | synthetic-demo | Labelled EirGrid-derived typical profile; not a live same-day forecast |
| Octopus Agile prices | running for configured GB regions | Live only when retrieval succeeds; unsupported/unpublished states are explicit |
| Flat and Economy 7 tariffs | running | User-entered, never labelled live |
| Robustness indicator | evidence-only | Transparent heuristic with parity tests; not calibrated |
| Conditional ex-post retro | synthetic-demo | Constructed curves; no observed adherence or customer outcome |
| Text, Excel, and PDF reports | built-local | Serialisation tests; optional report dependencies |
| dbt/Snowflake/Dagster/Power BI | built-local / synthetic-demo | Reproducible synthetic reporting path, not a connected production warehouse |
| Smart-meter ingestion and appliance control | designed-not-connected | Explicitly out of scope |
| Forecast-vintage benchmark | planned | Requires a new Gate 0 and licensed dataset |

Python tests cover optimisation, API validation/provenance, fallback behaviour, retro semantics, and report exports. CI also compiles the web client.

## Evidence boundary

All case-study, dashboard, and retro figures are synthetic-household demonstrations. Conditional ex-post analysis asks what the scheduled and baseline windows would have consumed under an altered curve. It does not observe schedule adherence and must not be described as realised customer savings.

See [CLAIM_LEDGER.md](CLAIM_LEDGER.md) and the [closeout evidence pack](evidence/credibility-closeout/).

## Freeze policy

After v0.2.0, in-scope maintenance is limited to:

- correctness and regression fixes;
- security and dependency maintenance;
- deployment reliability;
- documentation corrections that preserve the evidence boundary.

New product features, calibrated performance claims, and customer-outcome language remain out of scope until supported by observed data and a new project decision.
