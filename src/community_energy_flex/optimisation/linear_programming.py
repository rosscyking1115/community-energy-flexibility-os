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

from dataclasses import replace

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


def _band(value: float) -> str:
    return "Strong" if value >= 0.75 else "Mixed" if value >= 0.5 else "Fragile"


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

    # Score every task's feasible placements with the SAME scorer the rule-based
    # optimiser uses, so the two agree except for the LP's added constraints. The
    # per-placement score (0..1, lower is better) is the LP objective coefficient.
    feasible: dict[str, list[int]] = {}
    placements: dict[str, dict[int, object]] = {}
    scores: dict[str, dict[int, float]] = {}
    sorted_scores: dict[str, list[float]] = {}
    best_start: dict[str, int] = {}
    for task in tasks:
        starts = feasible_start_indices(task, num_slots)
        if not starts:
            continue
        placs = all_placements(task, slots, starts)
        scored = score_placements(task, placs, slots, objective, weights)  # best first
        feasible[task.task_id] = starts
        placements[task.task_id] = {p.start_index: p for p in placs}
        scores[task.task_id] = {sp.placement.start_index: sp.score for sp in scored}
        sorted_scores[task.task_id] = [sp.score for sp in scored]
        best_start[task.task_id] = scored[0].placement.start_index

    prob = pulp.LpProblem("energy_schedule", pulp.LpMinimize)
    x: dict[tuple[str, int], object] = {}
    for tid, starts in feasible.items():
        for s in starts:
            x[(tid, s)] = pulp.LpVariable(f"x_{tid}_{s}", cat="Binary")

    prob += pulp.lpSum(
        x[(tid, s)] * scores[tid][s] for tid, starts in feasible.items() for s in starts
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
        place = placements[tid][chosen]
        base = baseline_placement(task, slots)
        robustness = compute_robustness(
            sorted_scores[tid],
            horizon_hours=chosen * _SLOT_HOURS,
            using_measured_carbon=using_actual_carbon,
            tariff_is_manual=tariff_is_manual,
            single_option=len(starts) == 1,
        )
        # If a shared constraint (peak-load) forced this task off its own best
        # slot, don't report the landscape's strongest robustness - say so instead.
        if chosen != best_start[tid]:
            capped = min(robustness.value, 0.6)
            robustness = replace(
                robustness,
                value=capped,
                band=_band(capped),
                caveat="Constrained by the peak-load limit - not the standalone-best time.",
            )
        scheduled.append(
            ScheduledTask(
                task_id=tid, device_type=task.device_type,
                start_index=chosen, end_index=chosen + task.duration_slots,
                cost_p=place.cost_p, carbon_g=place.carbon_g,
                baseline_start_index=base.start_index,
                baseline_cost_p=base.cost_p, baseline_carbon_g=base.carbon_g,
                robustness_score=robustness.value,
                robustness_band=robustness.band,
                caveat=robustness.caveat,
            )
        )

    return Schedule(objective=objective, tasks=scheduled)
