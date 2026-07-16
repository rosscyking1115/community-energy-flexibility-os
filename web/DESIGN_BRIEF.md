# Design brief — Community Energy Flex website

This brief is the *why and how* for the visual build. The *what* (screens, flows,
data contract) lives in `web/UI_SPEC.md` — read that first and treat it as the
contract. This file adds product context, aesthetic direction, technical
constraints, and the verification gates the build must pass.

## 1. What this product is

A free, open-source planning tool that tells UK households and small community
organisations **when to run flexible electricity loads** (washing machine, EV
charge, dishwasher…) to cut cost and carbon. It is powered by live data: the
National Grid / NESO Carbon Intensity regional forecast (GB), Octopus Agile
half-hourly prices, and a typical-day carbon profile for Northern Ireland.

It is **decision support, not automation**: it recommends windows, shows the
saving versus the user's own baseline habit, and is honest about uncertainty
(robustness bands, caveats, a safety statement on every result).

## 2. Audience & tone

- Non-technical UK households — including people in or near energy poverty for
  whom "13p per wash" is a real number, not a rounding error. Also small
  community-hall / church / club operators planning shared loads.
- Tone: **calm, factual, respectful**. Like a well-designed utility bill or a
  Which? explainer — never like a fintech dashboard or a gamified eco app.
- Reading level: plain English. No jargon ("slot", "GSP", "intensity") without
  an inline explanation.

## 3. Aesthetic direction

The design should feel like a **trustworthy document, not a marketing site**.

- **Numbers are the interface.** Savings, times, rates, robustness — set them
  in tabular/monospaced numerals, give them typographic priority, and always
  pair each number with its basis (tariff + carbon source) per the
  score-beside-fact rule in UI_SPEC.
- **Editorial, not app-chrome.** Strong typographic hierarchy, generous
  whitespace, footnoted sources like a printed report. Avoid the
  shadcn/Tailwind-template look (centered hero, gradient blob, three feature
  cards) — this must read as designed, not scaffolded.
- **Palette: neutral first.** Warm paper/ink neutrals as the base; **one**
  restrained accent for interaction and recommended windows. Colour is never a
  verdict — no red=expensive/green=cheap encodings anywhere (UI_SPEC hard
  rule). Charts use neutral ink + the accent + shading, and always carry a
  second channel (labels/patterns) so colour is not the only signal.
- **No greenwash clichés.** No leaves, globes, wind-turbine hero photos, or
  eco-badge iconography. The sustainability story is told by the data.
- **The price/carbon curve is the signature visual.** A 48-half-hour day curve
  with recommended run-windows shaded and the baseline window marked. Design
  this one chart properly (axis labels in clock time, source footnote,
  keyboard/screen-reader accessible fallback table) and the product identity
  follows from it.
- Typeface direction: a characterful but highly legible text face paired with
  a tabular-numeral mono/semi-mono for figures. Self-host via `next/font`.
  Do not default to Inter-on-white.

## 4. Hard rules (restated — full list in UI_SPEC.md)

1. Indicators, never verdicts; always render `safety_statement`.
2. Savings beside assumptions, every time a figure appears.
3. Neutral colours; no good/bad colour coding.
4. Tabular numerals for every figure.
5. Sources footnoted (NESO Carbon Intensity, Octopus, EirGrid, appliance notes).
6. Explainability as tooltips/popovers, not a separate docs page.
7. Regional carbon is zonal — never imply postcode precision; label NI as
   typical-profile (`supports_live_forecast === false`).
8. Designed loading / empty / error states in product voice; surface the BFF's
   friendly 503 message, never a crash.

## 5. Technical constraints

- Next.js 15 App Router, React 19, TypeScript. Currently **plain CSS**
  (`app/globals.css`) — build the design system with CSS custom properties
  (design tokens) and CSS Modules per component. Do **not** add Tailwind or a
  component library; no UI kit should be visible in the result.
- **Do not change** `lib/api.ts`, `lib/types.ts`, `lib/proxy.ts`,
  `lib/config.ts`, or anything under `app/api/` (the BFF). Build components
  that consume the existing hooks and types.
- Server Components by default; `"use client"` only where interaction demands
  it (form controls, slider, chart hover). Keep the client bundle lean — the
  chart should be hand-rolled SVG, not a charting library.
- Replace/restyle `app/plan/page.tsx` freely (it is a deliberate placeholder);
  style `app/loading.tsx`, keep its role.
- Accessibility is a requirement, not a pass: WCAG AA contrast, full keyboard
  operation of the plan flow, labels on every control, `prefers-reduced-motion`
  respected, the curve chart has a data-table equivalent.
- Mobile-first: the plan flow must work one-handed on a small phone; the curve
  chart must degrade gracefully below ~360 px.

## 6. Verification gates (run these; the build isn't done until they pass)

```bash
cd web
npx tsc --noEmit
npm run lint
npm run build
```

Live check against the local API (`python -m uvicorn community_energy_api.main:app
--app-dir api --port 8000` from the repo root — bare `uvicorn` resolves the
wrong venv on this machine), then `npm run dev`. Verify the full flow: pick
region → add appliances → optimise → results render with safety statement,
sources, and shaded windows. **Note:** the preview screenshot tool is flaky in
this environment (renderer hangs) — verify with DOM snapshots/eval and curl,
and take screenshots only as best-effort proof.

## 7. Definition of done

- Home, Plan, and Methodology screens built per UI_SPEC flows.
- All eight hard rules verifiably satisfied on the Results view.
- Loading / empty / error states designed (kill the API mid-session and check).
- Gates in §6 green; no contract files touched.
- A short `web/DESIGN_NOTES.md` recording the aesthetic choices (tokens,
  type pairing, accent) so future work stays coherent.
