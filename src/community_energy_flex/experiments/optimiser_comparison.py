"""Compare optimiser strategies and (optionally) log the comparison to MLflow.

The comparison itself is a plain, testable function. MLflow logging is a thin
layer behind a guarded import, so the comparison runs and is tested without
MLflow installed. This is MLflow earning its place: real strategies, real
metrics, real artifacts.

    python -m community_energy_flex.experiments.optimiser_comparison
    # then:  mlflow ui   (requires the 'tracking' extra)
"""

from __future__ import annotations

import time
from dataclasses import dataclass

from community_energy_flex.domain.models import Objective, ObjectiveWeights, PlanningSlot, Task
from community_energy_flex.optimisation.linear_programming import optimise_lp
from community_energy_flex.optimisation.metrics import average_robustness, constraint_violations
from community_energy_flex.optimisation.rule_based import Schedule, optimise


@dataclass(frozen=True)
class ComparisonResult:
    optimiser: str  # "rule_based" | "lp"
    objective: str
    total_cost_saving_p: float
    total_carbon_saving_g: float
    avg_robustness: float
    constraint_violations: int
    runtime_s: float
    schedule: Schedule


def _result(name: str, tasks, schedule: Schedule, runtime_s: float) -> ComparisonResult:
    return ComparisonResult(
        optimiser=name,
        objective=str(schedule.objective),
        total_cost_saving_p=round(schedule.total_cost_saving_p, 3),
        total_carbon_saving_g=round(schedule.total_carbon_saving_g, 3),
        avg_robustness=round(average_robustness(schedule), 3),
        constraint_violations=constraint_violations(tasks, schedule),
        runtime_s=round(runtime_s, 5),
        schedule=schedule,
    )


def compare_optimisers(
    tasks: list[Task],
    slots: list[PlanningSlot],
    objectives: list[Objective] | None = None,
    weights: ObjectiveWeights | None = None,
    *,
    max_load_kw: float | None = None,
    using_actual_carbon: bool = False,
    tariff_is_manual: bool = True,
) -> list[ComparisonResult]:
    """Run the rule-based and LP optimisers for each objective and collect
    comparable metrics. Pure and network-free."""
    objectives = objectives or list(Objective)
    results: list[ComparisonResult] = []
    for objective in objectives:
        t0 = time.perf_counter()
        rb = optimise(
            tasks, slots, objective, weights,
            using_actual_carbon=using_actual_carbon, tariff_is_manual=tariff_is_manual,
        )
        results.append(_result("rule_based", tasks, rb, time.perf_counter() - t0))

        t0 = time.perf_counter()
        lp = optimise_lp(
            tasks, slots, objective, weights, max_load_kw=max_load_kw,
            using_actual_carbon=using_actual_carbon, tariff_is_manual=tariff_is_manual,
        )
        results.append(_result("lp", tasks, lp, time.perf_counter() - t0))
    return results


def log_comparison_to_mlflow(
    results: list[ComparisonResult],
    *,
    experiment_name: str = "schedule_optimisation",
    tracking_uri: str | None = None,
    extra_params: dict | None = None,
) -> None:
    """Log each comparison result as an MLflow run. Requires the 'tracking'
    extra:  pip install '.[tracking]'."""
    try:
        import mlflow
    except ImportError as exc:  # pragma: no cover - depends on env
        raise ImportError(
            "MLflow logging needs the 'tracking' extra: pip install '.[tracking]'"
        ) from exc

    if tracking_uri:
        mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(experiment_name)

    for r in results:
        with mlflow.start_run(run_name=f"{r.optimiser}-{r.objective}"):
            mlflow.log_params(
                {"optimiser": r.optimiser, "objective": r.objective, **(extra_params or {})}
            )
            mlflow.log_metrics(
                {
                    "total_cost_saving_p": r.total_cost_saving_p,
                    "total_carbon_saving_g": r.total_carbon_saving_g,
                    "avg_robustness": r.avg_robustness,
                    "constraint_violations": r.constraint_violations,
                    "runtime_seconds": r.runtime_s,
                }
            )
            lines = "\n".join(
                f"{st.task_id},{st.start_index},{st.end_index},{st.cost_p:.3f},{st.carbon_g:.3f}"
                for st in r.schedule.tasks
            )
            mlflow.log_text(
                "task_id,start,end,cost_p,carbon_g\n" + lines, "optimised_schedule.csv"
            )


def _main() -> int:  # pragma: no cover - thin CLI wrapper
    from community_energy_flex.demo import sample_carbon_curve, sample_tariffs, sample_tasks
    from community_energy_flex.optimisation.planning import build_planning_slots

    tariff = sample_tariffs()["Agile-style"]
    slots = build_planning_slots(sample_carbon_curve(), tariff)
    results = compare_optimisers(sample_tasks(), slots, tariff_is_manual=tariff.is_manual)

    print(f"{'optimiser':12} {'objective':14} {'cost_p':>8} {'carbon_g':>9} {'rob':>5} {'ms':>6}")
    for r in results:
        print(
            f"{r.optimiser:12} {r.objective:14} {r.total_cost_saving_p:8.2f} "
            f"{r.total_carbon_saving_g:9.1f} {r.avg_robustness:5.2f} {r.runtime_s * 1000:6.1f}"
        )
    try:
        log_comparison_to_mlflow(results, extra_params={"tariff": tariff.name})
        print("\nLogged to MLflow experiment 'schedule_optimisation'. Run: mlflow ui")
    except ImportError as exc:
        print(f"\n(MLflow not installed: {exc})")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(_main())
