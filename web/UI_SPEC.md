# Web UI spec — for the design build

The **plumbing is done** (BFF proxy, typed client, app-router shell, a working
but bare `/plan` page). This spec is for building the **visual UI** on top of it.
Don't change the data contract or the BFF; build components that consume the
hooks in `lib/api.ts` and the types in `lib/types.ts`.

## What's already wired (don't rebuild)

- `lib/api.ts` — `getRegions()`, `getAppliances()`, `optimise(req)`. They call
  same-origin `/api/*` BFF routes; never call the API origin directly.
- `lib/types.ts` — the contract (mirrors the API's pydantic models).
- `app/api/*` — BFF proxy route handlers. One error-shaping point.
- `app/loading.tsx` — style it, keep it.

## Screens

**Home (`app/page.tsx`)** — the honest-numbers promise; a "Plan tomorrow" CTA;
optional region auto-detect (by postcode via a future `/api/regions/by-postcode`).

**Plan (`app/plan/page.tsx`)** — the core tool. Flow:
1. Region select (`getRegions`). If `supports_live_forecast` is false (Northern
   Ireland), show a small "typical-day profile, not a live forecast" note.
2. Tariff: Agile (auto, when `supports_agile`) / Economy 7 / Flat / Manual.
3. Appliances: add from presets (`getAppliances`) as editable chips —
   energy, duration, and **clock-time** earliest/finish-by/preferred.
4. Objective: Cheapest / Lowest carbon / Balanced (cost↔carbon slider) / Avoid peak.
5. Results (`optimise`): per-appliance "run 02:30–04:00 **instead of** 06:00,
   saves 13p / 158 g · High", the price+carbon curve with recommended windows
   shaded, totals, a caveats panel, share/download.

**Methodology** — plain-language baseline/robustness (link to the repo docs).

## Non-negotiable design rules (from the product ethics principles)

- **Indicators, never verdicts.** Planning advice; caveats; never "guaranteed".
  Always render `safety_statement`.
- **Savings beside assumptions.** Never show a saving without the tariff + carbon
  basis next to it (the "score-beside-fact" rule).
- **Neutral colours.** No red=bad / green=good gradients — that *is* a verdict.
- **Tabular/mono numerals** for every figure (savings, times, rates).
- **Footnote the sources** (Carbon Intensity API/NESO, Octopus, EirGrid for NI,
  the appliance-figures note) like a document.
- **Explainability as tooltips**, not a docs page.
- **Region carbon is zonal** — say "South West region", never imply postcode
  precision. Label NI as typical-profile.
- Designed **loading / empty / error** states in product voice (the BFF already
  returns a friendly 503 detail on API outage — surface it, don't crash).

## Performance follow-up (optional, playbook §1)

For instant slider feel, mirror the optimiser's placement scoring in
`lib/scoring.ts` (TS mirror of `src/community_energy_flex/optimisation/objective.py`)
and re-rank locally when only the objective/weight changes — the curves come
from the server, the ordering recomputes on the client. Not required for v1.
