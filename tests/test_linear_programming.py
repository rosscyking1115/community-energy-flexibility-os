"""LP optimiser tests. The headline is peak-load coupling: a global constraint
the independent rule-based optimiser cannot express."""

from __future__ import annotations

import pytest

from community_energy_flex.data_sources.tariffs import FlatTariff
from community_energy_flex.demo import sample_carbon_curve, sample_tasks
from community_energy_flex.domain.models import Objective, Task
from community_energy_flex.optimisation.linear_programming import (
    InfeasibleScheduleError,
    optimise_lp,
    task_power_kw,
)
from community_energy_flex.optimisation.planning import build_planning_slots
from community_energy_flex.optimisation.rule_based import optimise

pytest.importorskip("pulp")


def _two_unit_tasks() -> list[Task]:
    # Two 1-slot, 1 kWh tasks -> 2 kW each. Both want the cheapest slot (2).
    return [
        Task("a", "load_a", energy_kwh=1.0, duration_slots=1, earliest_start=0, latest_finish=8),
        Task("b", "load_b", energy_kwh=1.0, duration_slots=1, earliest_start=0, latest_finish=8),
    ]


def _slot_loads(schedule, tasks, num_slots):
    power = {t.task_id: task_power_kw(t) for t in tasks}
    loads = [0.0] * num_slots
    for st in schedule.tasks:
        for i in range(st.start_index, st.end_index):
            loads[i] += power[st.task_id]
    return loads


def test_without_peak_limit_both_tasks_take_the_cheapest_slot(varied_slots):
    sched = optimise_lp(_two_unit_tasks(), varied_slots, Objective.CHEAPEST)
    assert sorted(st.start_index for st in sched.tasks) == [2, 2]  # both at cheapest


def test_peak_load_limit_forces_tasks_apart(varied_slots):
    # Each task is 2 kW; a 3 kW cap means they cannot share a slot.
    sched = optimise_lp(_two_unit_tasks(), varied_slots, Objective.CHEAPEST, max_load_kw=3.0)
    starts = sorted(st.start_index for st in sched.tasks)
    assert starts != [2, 2]  # can't both sit on the cheapest slot
    loads = _slot_loads(sched, _two_unit_tasks(), len(varied_slots))
    assert max(loads) <= 3.0 + 1e-6  # cap respected everywhere
    # One keeps the cheapest slot (2), the other takes the next cheapest (3).
    assert starts == [2, 3]


def test_all_must_run_tasks_scheduled_once(varied_slots):
    sched = optimise_lp(_two_unit_tasks(), varied_slots, Objective.BALANCED, max_load_kw=3.0)
    assert {st.task_id for st in sched.tasks} == {"a", "b"}


def test_infeasible_when_peak_limit_below_a_single_task(varied_slots):
    # A single 2 kW task cannot fit under a 1 kW cap.
    with pytest.raises(InfeasibleScheduleError):
        optimise_lp(_two_unit_tasks(), varied_slots, Objective.CHEAPEST, max_load_kw=1.0)


def test_lp_matches_rule_based_when_uncoupled():
    # With no shared constraint the LP and greedy optima are equally good. Assert
    # equal total carbon rather than identical starts: a long task over a flat
    # trough has genuine ties the two solvers may break differently.
    slots = build_planning_slots(sample_carbon_curve(), FlatTariff(unit_rate_p=28.0))
    tasks = sample_tasks()
    lp = optimise_lp(tasks, slots, Objective.LOWEST_CARBON)
    greedy = optimise(tasks, slots, Objective.LOWEST_CARBON)
    assert lp.total_carbon_g == pytest.approx(greedy.total_carbon_g)
