"""The MVP rule-based optimiser.

Each task is scheduled independently at its best-scoring feasible start (no
cross-task load constraint yet - that arrives with the LP/MILP optimiser in a
later milestone). Every recommendation carries a baseline comparison, a
robustness indicator, and a caveat.
"""

from __future__ import annotations

from community_energy_flex.domain.models import (
    Objective,
    ObjectiveWeights,
    PlanningSlot,
    Schedule,
    ScheduledTask,
    Task,
)
from community_energy_flex.optimisation.baseline import baseline_placement
from community_energy_flex.optimisation.energy_model import all_placements
from community_energy_flex.optimisation.feasible_windows import feasible_start_indices
from community_energy_flex.optimisation.objective import score_placements
from community_energy_flex.optimisation.robustness import compute_robustness

_SLOT_HOURS = 0.5

# ``Schedule`` now lives in the domain layer; re-exported here so existing
# ``from ...optimisation.rule_based import Schedule`` call sites keep working.
__all__ = ["Schedule", "optimise"]


def optimise(
    tasks: list[Task],
    slots: list[PlanningSlot],
    objective: Objective,
    weights: ObjectiveWeights | None = None,
    *,
    using_actual_carbon: bool = False,
    tariff_is_manual: bool = True,
) -> Schedule:
    weights = weights or ObjectiveWeights()
    scheduled: list[ScheduledTask] = []

    for task in tasks:
        starts = feasible_start_indices(task, len(slots))
        if not starts:  # optional task with no room
            continue
        placements = all_placements(task, slots, starts)
        scored = score_placements(task, placements, slots, objective, weights)
        best = scored[0].placement
        base = baseline_placement(task, slots)

        robustness = compute_robustness(
            [sp.score for sp in scored],
            horizon_hours=best.start_index * _SLOT_HOURS,
            using_measured_carbon=using_actual_carbon,
            tariff_is_manual=tariff_is_manual,
            single_option=len(scored) == 1,
        )

        scheduled.append(
            ScheduledTask(
                task_id=task.task_id,
                device_type=task.device_type,
                start_index=best.start_index,
                end_index=best.end_index,
                cost_p=best.cost_p,
                carbon_g=best.carbon_g,
                baseline_start_index=base.start_index,
                baseline_cost_p=base.cost_p,
                baseline_carbon_g=base.carbon_g,
                robustness_score=robustness.value,
                robustness_band=robustness.band,
                caveat=robustness.caveat,
            )
        )

    return Schedule(objective=objective, tasks=scheduled)
