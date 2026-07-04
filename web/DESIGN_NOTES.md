# Design notes — "After Midnight"

The realized design record for the web UI. Identity and tokens came from the
`frontend-design` pass (see `DESIGN_BRIEF_SUPPLEMENT.md`); this records what was
actually built and where.

## Identity: "the night band"
One signature device, reused with discipline: a **full-bleed 24-hour horizontal
band** (`components/DayBand.tsx`), midnight → midnight. Grid **carbon is ink
bars** encoded by height *and* ink density (`opacity = 0.42 + 0.53·t`) — never
colour. **Price is a thin ink line** (second channel). The **recommended
run-window is an amber bracket + label**; the **baseline is a dashed "usual"
tick**. It appears on the home hero (live, brackets tonight's real cleanest
window) and on `/plan` results (one bracket per appliance, stacked in tiers).

**The defining rule:** colour is never a verdict. Intensity is ink density;
amber (`--filament`) means one thing only — "run here". It is also the focus ring.

## Tokens (`app/globals.css`)
Palette: `--paper #E9EDF1` (cool dawn, not cream), `--paper-band #DDE3E9`,
`--panel #F1F4F7`, `--ink #1A1D21`, `--slate #5B636C` (AA 4.8:1 on paper),
`--curve #2E3A46` (bars), `--filament #E4A11B` (accent only), `--line #C9D2DB`,
`--line-strong #9AA6B1`. Amber only ever appears as a marker/wash, never as a
value scale.

## Type (`app/fonts.ts`)
IBM Plex Sans (display 700 / body 400–600) + IBM Plex Mono for **every figure**
(`.mono` sets `tabular-nums`). Self-hosted via `next/font` — no layout shift,
no runtime request. Numbers are the interface; each figure sits beside its
tariff + carbon-source basis.

## Data (real, not synthetic)
The band draws from a new API endpoint, `GET /v1/forecast/{region_id}`, added
for this build: the region's 48-slot carbon curve (live GB / EirGrid NI) plus
the Agile price curve where available. Home fetches it server-side
(`lib/server-data.ts`); `/plan` fetches via the BFF (`lib/api.ts` →
`app/api/forecast/[region]`). Windows, savings, confidence and the safety
statement all come from the real `POST /v1/optimise`. `lib/scoring.ts` only
parses the API's window strings and computes the home hero's honest "cleanest
window" from the real curve — no fabricated data anywhere.

## Component split
`DayBand` (pure SVG, Server-safe), `Masthead` (client, route-aware nav),
`BandLegend` (HTML legend above the SVG). Home & Methodology are Server
Components; `/plan` is the one client island (form state + the optimise call).

## States (all in product voice)
Loading = band + row shimmer skeleton (reduced-motion safe). Error =
region-load failure, plus a dedicated **422 overnight-window** explainer and a
**503 forecast-unavailable** message surfaced from the BFF. `aria-live`
announces working / ready / error.

## WCAG 2.2 AA
Full keyboard flow; amber focus ring with a 1px ink edge (≥3:1 on light paper);
skip link; `fieldset`/`legend` + real `<label>` on every control; the plan is a
`<form>` (submits on Enter); `role=radio`/`aria-checked` and `aria-pressed`;
targets ≥24px; the band carries a `Show data table` equivalent + descriptive
`aria-label`; colour never the sole signal; `prefers-reduced-motion` respected.

## Known follow-ups
- Page-level styles are token-driven inline styles (`DayBand`/`Masthead` use CSS
  Modules); the dense page content could be extracted into `.module.css` files
  for parity with the component layer.
- Tariff options are Agile / Economy 7 / Flat (real, working). "Manual
  half-hourly" was omitted pending a rate-entry UI, since it needs 48 values to
  produce a valid request.
- The `DayBand` has no hover read-out yet (the spec lists it as optional); the
  data table is the accessible equivalent.
