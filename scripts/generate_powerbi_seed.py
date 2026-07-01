"""Generate dbt seed data for the Power BI reporting star.

Runs the real rule-based optimiser over a two-week window for a handful of
demo households and writes per-task daily savings to
``dbt_energy/seeds/seed_daily_savings.csv``. Deterministic (seeded per
household/day) so the seed is reproducible.

Usage:
    PYTHONPATH=src python scripts/generate_powerbi_seed.py
Then rebuild and re-export:
    cd dbt_energy && dbt build
    (see docs/POWERBI_DASHBOARD_GUIDE.md step 0 for the CSV export)
"""

from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path

from community_energy_flex.data_sources.tariffs import multiband_from_half_hour_prices
from community_energy_flex.demo import sample_carbon_curve, sample_tasks
from community_energy_flex.domain.models import SLOTS_PER_DAY, Objective, Task
from community_energy_flex.optimisation.planning import DEFAULT_PEAK_SLOTS, build_planning_slots
from community_energy_flex.optimisation.rule_based import optimise

OUT = Path(__file__).resolve().parents[1] / "dbt_energy" / "seeds" / "seed_daily_savings.csv"

COMMUNITIES = [("C1", "Riverside Centre"), ("C2", "Hilltop Community")]
HOUSEHOLDS_PER_COMMUNITY = 2
DAYS = 14
START = date(2026, 6, 24)


def demo_tasks() -> list[Task]:
    """The household's flexible loads. The tumble dryer's *baseline* sits inside
    the 17:00-19:00 peak (preferred 17:30), so shifting it produces a real
    peak_slots_avoided signal - the other tasks live outside the peak."""
    return [
        *sample_tasks(),
        Task(
            task_id="tumble_dryer",
            device_type="Tumble dryer",
            energy_kwh=2.0,
            duration_slots=3,  # 1.5 hours
            earliest_start=28,  # 14:00
            latest_finish=46,  # by 23:00
            preferred_start=35,  # 17:30 - inside the evening peak
        ),
    ]


def peak_overlap(start: int, duration: int) -> int:
    return sum(1 for i in range(start, start + duration) if i in DEFAULT_PEAK_SLOTS)


def main() -> int:
    base_curve = sample_carbon_curve()
    tasks = demo_tasks()
    rows: list[list] = []

    for d in range(DAYS):
        day = START + timedelta(days=d)
        for cid, _cname in COMMUNITIES:
            for h in range(1, HOUSEHOLDS_PER_COMMUNITY + 1):
                hh = f"{cid}-H{h}"
                rng = random.Random(f"{day}{hh}")
                # deterministic per-household/day variation of the carbon day
                shift = rng.randint(-3, 3)
                scale = rng.uniform(0.9, 1.15)
                curve = [
                    max(20.0, base_curve[(i + shift) % SLOTS_PER_DAY] * scale)
                    for i in range(SLOTS_PER_DAY)
                ]
                prices = [max(5.0, c / 12.0) for c in curve]
                tariff = multiband_from_half_hour_prices(
                    prices, standing_charge_p=45.0, is_manual=False
                )
                slots = build_planning_slots(curve, tariff)
                schedule = optimise(tasks, slots, Objective.BALANCED, tariff_is_manual=False)

                for st in schedule.tasks:
                    duration = st.end_index - st.start_index
                    avoided = max(
                        0,
                        peak_overlap(st.baseline_start_index, duration)
                        - peak_overlap(st.start_index, duration),
                    )
                    rows.append(
                        [
                            day.isoformat(), cid, hh, st.device_type,
                            round(st.baseline_cost_p, 2), round(st.cost_p, 2),
                            round(st.cost_saving_p, 2), round(st.carbon_saving_g, 1),
                            avoided, st.confidence, st.confidence_band,
                        ]
                    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                "savings_date", "community_id", "household_id", "device_type",
                "baseline_cost_p", "optimised_cost_p", "cost_saving_p",
                "carbon_saving_g", "peak_slots_avoided", "confidence",
                "confidence_band",
            ]
        )
        writer.writerows(rows)

    days = len({r[0] for r in rows})
    households = len({r[2] for r in rows})
    total_avoided = sum(r[8] for r in rows)
    print(
        f"{OUT.name}: {len(rows)} rows over {days} days, {households} households, "
        f"{total_avoided} peak slots avoided in total"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
