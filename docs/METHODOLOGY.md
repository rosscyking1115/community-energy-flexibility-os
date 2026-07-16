# Methodology

The engine answers a bounded question: given a flexible task, a half-hourly carbon curve, a tariff, and a feasible time window, which start time best matches the selected objective relative to an explicit baseline?

## Planning unit and feasibility

One slot is 30 minutes. A task defines energy, duration, earliest start, latest finish, and a preferred start. A candidate is feasible only when every occupied slot is inside the task window. LP/MILP mode can also enforce shared-capacity and overlap constraints.

Energy is spread evenly across the occupied slots. This is a simplifying load-shape assumption, not device telemetry.

## Cost and carbon

For slot `i`:

```text
slot_energy_kwh = task_energy_kwh / duration_slots
cost_p = sum(slot_energy_kwh * unit_rate_p_per_kwh[i])
carbon_g = sum(slot_energy_kwh * carbon_g_per_kwh[i])
```

Standing charges are excluded because shifting a task does not change them.

## Baseline and savings

The baseline is the same task at its feasible preferred start. It is not a population counterfactual or a claim about what a household would otherwise have done.

```text
estimated_cost_saving = baseline_cost - recommended_cost
estimated_carbon_saving = baseline_carbon - recommended_carbon
```

Negative values remain visible. The optimiser does not turn an unfavourable comparison into a positive claim.

## Objectives

- **Cost:** minimise estimated task cost.
- **Carbon:** minimise estimated task carbon.
- **Balanced:** combine normalised cost and carbon ranks.

Ties are deterministic so identical inputs produce identical schedules.

## Robustness indicator

The indicator is the product of four bounded factors:

- decisiveness of the chosen window relative to alternatives;
- forecast horizon;
- carbon-data quality;
- tariff-data quality.

It is banded **Strong**, **Mixed**, or **Fragile**. The exact formula is transparent in `optimisation/robustness.py`, but the result is not a probability and has not been calibrated against observed outcomes. Every result includes a caveat describing the limiting inputs.

## Conditional ex-post analysis

The retro workflow replaces the planning carbon curve with a synthetic altered curve, then recomputes the scheduled and baseline windows. This provides a conditional ex-post comparison: *if both starts and the task load shape were as assumed, what would their relative carbon have been under that curve?*

The workflow does not observe task execution. `schedule_adherence_observed` is therefore false. Its output is a synthetic stress test and must not be described as realised household savings.

## Limitations

- No appliance control, smart-meter ingestion, or schedule-adherence observation.
- Uniform task load shapes.
- Manual/sample tariffs unless a caller supplies another curve.
- Northern Ireland and provider-failure paths use labelled profiles rather than live forecasts.
- No calibrated guarantee of savings, recommendation correctness, or user behaviour.
