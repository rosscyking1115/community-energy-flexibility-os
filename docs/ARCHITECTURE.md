# Architecture

## Layers

```
domain/        pure data types + invariants (Task, Schedule, PlanningSlot, ...)
   ▲
data_sources/  carbon-intensity client + tariff models (I/O isolated, parsers pure)
optimisation/  feasible windows → energy model → objective → robustness → optimiser
reporting/     ActionSummary (one source of truth) → text / Excel / PDF renderers
monitoring/    run store (CSV) + forecast-vs-actual retro loop
pipeline/      daily run as injected, testable functions (keep-last-good fallback)
   ▲
orchestration/ Dagster assets/jobs/schedules — thin wrappers, no logic
app/           Streamlit decision app
```

Dependencies point **inward**: everything may depend on `domain`; nothing in
`domain` depends outward.

## Design principles applied

- **Deep modules, thin seams.** The pipeline's logic lives in plain functions
  with all I/O injected; Dagster is a wrapper. The energy model
  (`evaluate_placement`) is one small primitive reused by the optimiser,
  baseline, and retro loop.
- **One source of truth for output.** `reporting/summary.py::ActionSummary` is
  built once; Excel, PDF, text, and the app all render from it, so the numbers
  and wording can never drift between formats.
- **Isolate I/O behind pure cores.** The carbon client separates HTTP from
  parsing, so parsing is unit-tested against fixture JSON with no network.

## Review findings (Milestone B)

A deep-module / deletion-test pass over `optimisation/` and `reporting/`:

| Module | Verdict |
|---|---|
| `energy_model` | Deep, widely reused primitive — keep. |
| `objective`, `robustness` | Substantial logic behind a small interface — keep. |
| `feasible_windows`, `baseline` | Small but each owns a named domain concept with good locality — keep. |
| `reporting/summary` | Good seam; Excel/PDF are thin renderers — keep. |

**One change made — ADR-001 below.**

### ADR-001: `Schedule` moves to the domain layer

**Context.** `Schedule` (the full optimisation result) was defined inside
`optimisation/rule_based.py`, but `reporting`, `pipeline`, and `monitoring/retro`
all imported it — three modules depending on the optimiser's *implementation
file* just to name a result type.

**Decision.** Move `Schedule` to `domain/models.py` alongside `ScheduledTask`.
`rule_based.py` re-exports it for backward compatibility; consumers now import it
from the domain.

**Consequence.** The shared result type lives with the other domain types;
downstream modules depend on the stable domain, not on the optimiser. When the
LP/MILP optimiser lands in Milestone C it produces the same `Schedule` with no
change to reporting, pipeline, or retro.
