"""Mixed-integer LP optimiser (PuLP/CBC).

The rule-based optimiser schedules each task independently. The real value of an
LP is *coupling*: it schedules all tasks jointly under shared constraints the
rule-based solver cannot express - most importantly a **peak-load limit** (don't
draw more than N kW at once), plus must-run-once and per-task deadlines
(EV-charged-by, must-finish-before). It returns the same :class:`Schedule`
domain type, so reporting, the pipeline, and the retro loop use it unchanged.

Requires the ``optim`` extra:  pip install '.[optim]'
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
from community_energy_flex.optimisation.confidence import compute_confidence
from community_energy_flex.optimisation.energy_model import all_placements
from community_energy_flex.optimisation.feasible_windows import feasible_start_indices
from community_energy_flex.optimisation.objective import score_placements

_SLOT_HOURS = 0.5


class InfeasibleScheduleError(RuntimeError):
    """Raised when no schedule satisfies the constraints (e.g. peak-load too low
    for the must-run tasks)."""


def _require_pulp():
    try:
        import pulp
    except ImportError as exc:  # pragma: no cover - depends on env
        raise ImportError(
            "The LP optimiser needs PuLP. Install with: pip install '.[optim]'"
        ) from exc
    # PuLP 3.x emits v4-migration DeprecationWarnings for LpVariable/LpProblem/
    # PULP_CBC_CMD. The bundled API still works; silence via PuLP's own flag.
    try:
        from pulp import v4_migration

        v4_migration.V4_MIGRATION_WARNINGS = False
    except Exception:  # pragma: no cover - flag may move between versions
        pass
    return pulp


def task_power_kw(task: Task) -> float:
    """Average power drawn while the task runs (kW)."""
    return task.energy_per_slot_kwh / _SLOT_HOURS


def _placement_coefficient(
    cost_p: float, carbon_g: float, comfort: float,
    objective: Objective, weights: ObjectiveWeights,
    cost_scale: float, carbon_scale: float,
) -> float:
    """Linear objective coefficient for a placement (lower is better)."""
    nc, ncarb = cost_p / cost_scale, carbon_g / carbon_scale
    if objective is Objective.CHEAPEST:
        return cost_p
    if objective is Objective.LOWEST_CARBON:
        return carbon_g
    if objective is Objective.BALANCED:
        total_w = weights.cost + weights.carbon + weights.comfort
        return (weights.cost * nc + weights.carbon * ncarb + weights.comfort * comfort) / total_w
    if objective is Objective.AVOID_PEAK:
        return 0.5 * nc + 0.5 * ncarb  # peak handled as a hard constraint below
    raise ValueError(f"unknown objective {objective}")


def optimise_lp(
    tasks: list[Task],
    slots: list[PlanningSlot],
    objective: Objective,
    weights: ObjectiveWeights | None = None,
    *,
    max_load_kw: float | None = None,
    using_actual_carbon: bool = False,
    tariff_is_manual: bool = True,
) -> Schedule:
    pulp = _require_pulp()
    weights = weights or ObjectiveWeights()
    num_slots = len(slots)

    # Pre-compute every task's feasible placements and comfort penalties.
    feasible: dict[str, list[int]] = {}
    placements: dict[str, dict[int, object]] = {}
    comfort: dict[str, dict[int, float]] = {}
    all_cost, all_carbon = [1e-9], [1e-9]
    for task in tasks:
        starts = feasible_start_indices(task, num_slots)
        if not starts:
            continue
        feasible[task.task_id] = starts
        placements[task.task_id] = {p.start_index: p for p in all_placements(task, slots, starts)}
        span = max(starts) - min(starts)
        has_pref = task.preferred_start is not None and span
        comfort[task.task_id] = {
            s: (abs(s - task.preferred_start) / span if has_pref else 0.0) for s in starts
        }
        all_cost += [p.cost_p for p in placements[task.task_id].values()]
        all_carbon += [p.carbon_g for p in placements[task.task_id].values()]

    cost_scale, carbon_scale = max(all_cost), max(all_carbon)

    prob = pulp.LpProblem("energy_schedule", pulp.LpMinimize)
    x: dict[tuple[str, int], object] = {}
    for tid, starts in feasible.items():
        for s in starts:
            x[(tid, s)] = pulp.LpVariable(f"x_{tid}_{s}", cat="Binary")

    # Objective.
    prob += pulp.lpSum(
        x[(tid, s)] * _placement_coefficient(
            placements[tid][s].cost_p, placements[tid][s].carbon_g,
            comfort[tid][s], objective, weights, cost_scale, carbon_scale,
        )
        for tid, starts in feasible.items()
        for s in starts
    )

    # Each task runs once (must_run) or at most once (optional).
    tasks_by_id = {t.task_id: t for t in tasks}
    for tid, starts in feasible.items():
        total = pulp.lpSum(x[(tid, s)] for s in starts)
        prob += (total == 1) if tasks_by_id[tid].must_run else (total <= 1)

    # Peak-load limit: total power drawn in any slot must not exceed max_load_kw.
    if max_load_kw is not None:
        power = {tid: task_power_kw(tasks_by_id[tid]) for tid in feasible}
        for t in range(num_slots):
            load = pulp.lpSum(
                x[(tid, s)] * power[tid]
                for tid, starts in feasible.items()
                for s in starts
                if s <= t < s + tasks_by_id[tid].duration_slots
            )
            prob += load <= max_load_kw, f"peak_slot_{t}"

    status = prob.solve(pulp.PULP_CBC_CMD(msg=0))
    if pulp.LpStatus[status] != "Optimal":
        raise InfeasibleScheduleError(
            f"no feasible schedule (solver status: {pulp.LpStatus[status]}); "
            "the peak-load limit may be too low for the must-run tasks"
        )

    # Build the Schedule from the chosen starts.
    scheduled: list[ScheduledTask] = []
    for tid, starts in feasible.items():
        chosen = next(s for s in starts if round(pulp.value(x[(tid, s)])) == 1)
        task = tasks_by_id[tid]
        best = placements[tid][chosen]
        base = baseline_placement(task, slots)
        scored = score_placements(task, list(placements[tid].values()), slots, objective, weights)
        conf = compute_confidence(
            [sp.score for sp in scored],
            horizon_hours=chosen * _SLOT_HOURS,
            using_actual_carbon=using_actual_carbon,
            tariff_is_manual=tariff_is_manual,
            single_option=len(starts) == 1,
        )
        scheduled.append(
            ScheduledTask(
                task_id=tid, device_type=task.device_type,
                start_index=chosen, end_index=chosen + task.duration_slots,
                cost_p=best.cost_p, carbon_g=best.carbon_g,
                baseline_start_index=base.start_index,
                baseline_cost_p=base.cost_p, baseline_carbon_g=base.carbon_g,
                confidence=conf.value, confidence_band=conf.band, caveat=conf.caveat,
            )
        )

    return Schedule(objective=objective, tasks=scheduled)
