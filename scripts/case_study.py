"""Reproducible synthetic scenario behind docs/CASE_STUDY.md.

Runs the optimiser on constructed community-centre-style inputs for one day.
The scenario is illustrative; it is not evidence from an actual organisation.

    PYTHONPATH=src python scripts/case_study.py
"""

from __future__ import annotations

import sys

from community_energy_flex.demo import sample_carbon_curve, sample_tariffs
from community_energy_flex.domain.models import Objective, Task, slot_to_time
from community_energy_flex.monitoring.retro import evaluate_retrospective
from community_energy_flex.optimisation.planning import build_planning_slots
from community_energy_flex.optimisation.rule_based import optimise

# Render £ and other symbols cleanly whatever the console's default codec is
# (Windows terminals default to cp1252 and would otherwise mojibake the £).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Riverside Community Centre - tomorrow's flexible loads. Times are half-hour
# slots (13:00 = 26). "preferred" is what staff would do without the tool.
TASKS = [
    Task("dishwasher", "Commercial dishwasher", energy_kwh=3.0, duration_slots=3,
         earliest_start=26, latest_finish=44, preferred_start=27),      # after lunch club
    Task("water_heater", "Water heater", energy_kwh=4.0, duration_slots=4,
         earliest_start=0, latest_finish=16, preferred_start=12),       # ready by 08:00
    Task("minibus", "Minibus EV charge", energy_kwh=20.0, duration_slots=10,
         earliest_start=0, latest_finish=15, preferred_start=0),        # charged by 07:30
    Task("scrubber", "Floor scrubber charge", energy_kwh=1.5, duration_slots=2,
         earliest_start=0, latest_finish=16, preferred_start=12),
]


def main() -> int:
    forecast = sample_carbon_curve()
    tariff = sample_tariffs()["Agile-style"]  # half-hourly, tracks the market
    slots = build_planning_slots(forecast, tariff)

    schedule = optimise(TASKS, slots, Objective.BALANCED, tariff_is_manual=False)

    print("Riverside Community Centre - recommended plan (balanced)\n")
    for st in schedule.tasks:
        print(
            f"  {st.device_type:24} run {slot_to_time(st.start_index)}-{slot_to_time(st.end_index)}"
            f"  (was {slot_to_time(st.baseline_start_index)})"
            f"  saves {st.cost_saving_p:5.1f}p / {st.carbon_saving_g:6.0f} g"
            f"  [{st.robustness_band} robustness]"
        )

    day_cost = schedule.total_cost_saving_p / 100
    day_carbon = schedule.total_carbon_saving_g / 1000
    print(f"\n  Daily total: £{day_cost:.2f} and {day_carbon:.2f} kg CO2")
    # Retro: actual carbon came in ~8% dirtier overnight than forecast.
    actual = [c * 1.08 for c in forecast]
    actual_slots = build_planning_slots(actual, tariff)
    retro = evaluate_retrospective(
        TASKS, schedule, actual_slots, forecast_curve=forecast, actual_curve=actual
    )
    print(
        f"\n  Synthetic stress test (later curve 8% dirtier): conditional ex-post ratio "
        f"{retro.conditional_ex_post_carbon_fraction * 100:.0f}% of forecast saving; "
        f"forecast MAE {retro.carbon_forecast_mae:.0f} gCO2/kWh"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
