# Design brief — supplement (distinctiveness pass)

Read **`web/DESIGN_BRIEF.md`** and **`web/UI_SPEC.md`** first; this does not
replace them. It adds the one thing they were missing: a **specific aesthetic
direction** and a set of **acceptance criteria** you can apply directly. Every
rule below is plain judgment — no commands, no tools, no installs required.

It exists because the current build reads as **templated**. The job of this
pass is to give the product a visual identity that could not be mistaken for
any other tool.

---

## 0. The trap to escape

AI-generated UI right now clusters on three looks. Avoid all three:

1. Warm cream (~`#F4F1EA`) + high-contrast serif display + terracotta accent.
2. Near-black background + one acid-green / vermilion accent.
3. Broadsheet layout: hairline rules, zero radius, dense newspaper columns.

> Note: the *original* `DESIGN_BRIEF.md` leaned toward #3 ("trustworthy
> document", footnotes, hairline rules). That instinct — calm, honest, factual
> — is right; the *broadsheet execution* is the default. Keep the instinct,
> drop the newspaper. The organising device is the time-band below, not ruled
> columns.

---

## 1. Direction: "The night band"

**Subject anchor.** The real artifact in this product's world is *the
half-hourly day* — 48 slots of grid carbon and price, midnight to midnight.
The materials are meter readings, tariff sheets, the amber glow of a
night-storage timer, the "small hours" when off-peak lives. The page's single
job: show a household the cleanest/cheapest window to run a load tonight,
honestly.

**Signature element (the one memorable thing).** A **full-bleed 24-hour
horizontal band**, midnight → midnight mapped left → right. The carbon/price
shape is drawn in *ink* (line + faint fill); the recommended run-window is
marked with an **amber bracket + label** ("run 02:30–04:00"). Use it as:
- the **home hero** — live for a default region, already bracketing tonight's
  best window (a live demo, *not* a big-number-with-label hero); and
- the **`/plan` results view** — the same band, with the user's appliances
  placed as brackets on it.

One device, reused with discipline. It *is* the identity.

**Tokens** (derive every colour/type decision from these):

| Role | Value |
|---|---|
| Paper (bg) | `#E9EDF1` — a cool "dawn" grey-blue, deliberately **not** warm cream |
| Ink (text) | `#1A1D21` |
| Slate (captions/labels) | `#5B636C` |
| Curve (band stroke/fill) | `#2E3A46` |
| **Filament (accent)** | `#E4A11B` — amber; the **only** accent, used *solely* for the "run here" marker and the focus ring |

| Type role | Face |
|---|---|
| Display | **IBM Plex Sans**, heavy weight, tight tracking |
| Body | **IBM Plex Sans** |
| Data / figures | **IBM Plex Mono** — tabular numerals; every number (rates, times, savings) is set in this |

Self-host all three with `next/font` (no layout shift, no external request).
The Plex superfamily is a *choice*: it carries the engineering/meter vernacular
of the subject and is not the Inter/serif default.

**The one aesthetic risk (justified):** intensity on the band is encoded by
**ink density / line height — never colour**. Most energy UIs colour-code
green=clean / red=dirty; we do not, because *colour is never a verdict* (a core
product ethic). Amber therefore stays reserved purely as the "run here" marker.
The constraint becomes the identity.

**If you adapt the motif**, keep these invariants — they, not the exact drawing,
are what defeat "templated":
- time maps to horizontal space, full-bleed, breaking the text column;
- numbers are the interface (mono, tabular, always beside their basis);
- exactly one accent, used only to say "act here", never to grade good/bad;
- the hero is a live recommendation, not a marketing hero.

---

## 2. Component & code criteria (composition + Next.js)

Component API rules (from the `vercel-composition-patterns` skill — the exact
rule names are given so they're checkable):

- **`architecture-avoid-boolean-props`** — do not add boolean props to
  customise behaviour (`isPrimary`, `isLarge`, `hasIcon`, `showBaseline`…).
  Compose instead.
- **`patterns-explicit-variants`** — where behaviour really does branch, make
  explicit variant components, not boolean modes. e.g. `<RunWindow>` and
  `<PeakWindow>` rather than `<Window isPeak>`.
- **`patterns-children-over-render-props`** — pass `children` for composition
  rather than `renderX` props.
- **`architecture-compound-components`** — for anything with shared state (the
  plan form driving the band), use a compound component with a context
  provider, not one prop-drilled mega-component.
- **`state-lift-state` / `state-decouple-implementation` / `state-context-interface`**
  — the plan's state (region, tariff, tasks, objective, result) lives in one
  provider exposing a generic `{ state, actions, meta }` interface; the band and
  the form are siblings that read from it. The provider is the only place that
  knows *how* state is stored.
- **`react19-no-forwardref`** — this app is React 19: do **not** use
  `forwardRef`; pass `ref` as a normal prop, and use `use()` rather than
  `useContext()`.
- **Split by responsibility:** `<DayBand>` (draw), `<RunWindow>` (a bracket),
  `<FigureRow>` (a labelled tabular number + its basis), `<RegionPicker>`,
  `<AppliancePicker>` — not one page component that does everything.

Next.js / rendering:

- **Server Components by default; `"use client"` only at the interactive
  leaves** (form controls, the band's hover/focus). The home hero band can be a
  Server Component that fetches once; keep the `/plan` tool client-side as it
  already is.
- **Hand-roll the band as SVG.** No charting library, no Tailwind, no UI kit —
  CSS custom properties + CSS Modules, per `DESIGN_BRIEF.md`.
- **Real states, in product voice:** style `loading.tsx`; add an
  `error.tsx`/inline error that surfaces the BFF's friendly 503 detail; design
  the empty state (no appliances yet) as an invitation to act, not a blank box.
- Keep the client bundle lean; dynamically import anything heavy that's
  client-only.

---

## 3. Accessibility acceptance (WCAG 2.2 AA — tool-free checklist)

From the `accessibility` skill (WCAG 2.2). Grouped POUR; the "new in 2.2"
criteria are called out because they're the ones most builds miss.

**Perceivable**
- **Contrast** (§1.4.3/§1.4.11): body text ≥ 4.5:1; large text ≥ 3:1; the band
  stroke, the Filament focus ring, and form borders ≥ 3:1 as non-text UI.
  → verify `#5B636C` slate on `#E9EDF1` paper hits 4.5:1; darken if not.
- **Never rely on colour alone** (§1.4.1) — the band encodes intensity by ink
  density and the amber marker also carries a text label ("run 02:30–04:00").
- **Text/table equivalent for the band** (§1.1.1): a real (visually-available
  or visually-hidden) table of slot → time → p/kWh → gCO₂; decorative SVG parts
  get `aria-hidden="true"`.

**Operable**
- **Full keyboard operation** of the whole plan flow; prefer native `<button>`,
  `<a href>`, `<select>`, `<input>` over `div[role]` (§2.1.1); no keyboard
  traps (§2.1.2).
- **Focus visible** via `:focus-visible` using the Filament ring (§2.4.7);
  never `outline: none` without a replacement.
- **Focus not obscured** by sticky headers/overlays — use `scroll-margin`
  (§2.4.11, *new in 2.2*).
- **Skip link** to main content (§2.4.1).
- **Target size ≥ 24×24px** for every interactive element (§2.5.8, *new in
  2.2*).
- If the band uses drag to place a window, provide a **single-pointer / typed
  alternative** (§2.5.7, *new in 2.2*).
- **`prefers-reduced-motion` respected** for any band draw-in or transitions
  (§2.3).

**Understandable**
- **Page language** set (§3.1.1) — `layout.tsx` already has `lang="en-GB"`,
  keep it.
- **Form labels** programmatically associated with every control (§3.3.2);
  inputs submit on Enter.
- **Error handling** (§3.3.1/§3.3.3): `role="alert"`, `aria-invalid="true"` on
  the bad field, focus the first error on submit; say what's wrong and how to
  fix it. Surface the API's 422 (e.g. overnight wrap window) this way.
- **Consistent help** in the same relative position across pages (§3.2.6, *new
  in 2.2*); **no redundant re-entry** of values already given in the session
  (§3.3.7, *new in 2.2*).

**Robust**
- **Live regions** (§4.1.3): "Working…", "results ready", and errors announced
  via `aria-live` — never a sighted-only change.
- **Correct roles/names/values** (§4.1.2); native elements first, ARIA only
  when there's no native equivalent.

---

## 4. Definition of done (observable — no commands)

- Home, `/plan`, and Methodology built on the "night band" identity.
- The eight ethics rules from `UI_SPEC.md` visibly satisfied on Results
  (safety statement rendered; every saving shown beside its tariff + carbon
  basis; neutral colour; tabular numerals; sources footnoted; NI labelled as
  typical-profile).
- Loading / empty / error states designed and reachable.
- No file under `lib/` or `app/api/` changed; no Tailwind or component library
  present.
- A short `web/DESIGN_NOTES.md` records the final palette, type pairing, and
  the reasoning for the signature — so future work stays coherent.
