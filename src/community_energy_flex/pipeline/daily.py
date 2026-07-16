"""The daily optimisation pipeline.

Steps: fetch carbon forecast -> validate -> optimise -> record monitoring, with a
keep-last-good-schedule fallback so a bad forecast pull never leaves users with
nothing. All I/O (the carbon fetch, the stores) is injected, so the whole thing
runs in tests with no network and no scheduler.
"""

from __future__ import annotations

import json
import time
import uuid
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol

from community_energy_flex.data_sources.tariffs import Tariff
from community_energy_flex.domain.models import (
    SLOTS_PER_DAY,
    Objective,
    ObjectiveWeights,
    Schedule,
    ScheduledTask,
    Task,
)
from community_energy_flex.monitoring.store import (
    DataFreshness,
    OptimisationQuality,
    PipelineRun,
)
from community_energy_flex.optimisation.metrics import average_robustness, constraint_violations
from community_energy_flex.optimisation.planning import build_planning_slots
from community_energy_flex.optimisation.rule_based import optimise


# --- keep-last-good-schedule stores -----------------------------------------
class LastGoodStore(Protocol):
    def save(self, schedule: Schedule) -> None: ...
    def load(self) -> Schedule | None: ...


class InMemoryLastGoodStore:
    def __init__(self) -> None:
        self._schedule: Schedule | None = None

    def save(self, schedule: Schedule) -> None:
        self._schedule = schedule

    def load(self) -> Schedule | None:
        return self._schedule


class JsonLastGoodStore:
    """Persists the last good schedule to disk so a fallback survives restarts.

    Uses JSON rather than pickle: the artifact stays inert, so loading it can
    never execute code even if the file on disk is tampered with. The schedule
    is a flat tree of dataclasses over primitives, so it round-trips cleanly.
    """

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def save(self, schedule: Schedule) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "objective": str(schedule.objective),
            "tasks": [asdict(t) for t in schedule.tasks],
        }
        self.path.write_text(json.dumps(payload), encoding="utf-8")

    def load(self) -> Schedule | None:
        if not self.path.exists():
            return None
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        return Schedule(
            objective=Objective(payload["objective"]),
            tasks=[ScheduledTask(**task) for task in payload["tasks"]],
        )


# --- steps ------------------------------------------------------------------
class DataValidationError(ValueError):
    """Raised when a fetched carbon curve is unusable."""


def fetch_carbon_forecast(fetcher: Callable[[], list[float]]) -> list[float]:
    """Run the injected fetcher. Any failure propagates as an exception for the
    pipeline's fallback to catch."""
    return fetcher()


def validate_carbon_curve(curve: list[float], expected_slots: int = SLOTS_PER_DAY) -> None:
    if len(curve) < expected_slots:
        raise DataValidationError(
            f"carbon curve has {len(curve)} slots, need {expected_slots} "
            "(forecast missing for tomorrow)"
        )
    if any(v is None or v < 0 for v in curve[:expected_slots]):
        raise DataValidationError("carbon curve contains missing or negative values")


# --- orchestrated run -------------------------------------------------------
@dataclass
class DailyPipelineConfig:
    tasks: list[Task]
    tariff: Tariff
    objective: Objective = Objective.BALANCED
    weights: ObjectiveWeights = field(default_factory=ObjectiveWeights)
    carbon_fetcher: Callable[[], list[float]] | None = None
    using_actual_carbon: bool = False
    job: str = "daily_energy_optimisation"


@dataclass(frozen=True)
class PipelineResult:
    run_id: str
    status: str  # "success" | "fallback" | "failed"
    schedule: Schedule | None
    message: str = ""


def run_daily_pipeline(
    config: DailyPipelineConfig,
    *,
    store=None,
    last_good: LastGoodStore | None = None,
) -> PipelineResult:
    run_id = uuid.uuid4().hex[:12]
    started = time.perf_counter()
    fetcher = config.carbon_fetcher
    if fetcher is None:
        raise ValueError("config.carbon_fetcher must be provided")

    def _record_run(status: str, rows: int, message: str) -> None:
        if store is not None:
            store.record(
                PipelineRun(
                    run_id=run_id, job=config.job, status=status,
                    duration_s=round(time.perf_counter() - started, 4),
                    rows_ingested=rows, message=message,
                )
            )

    try:
        curve = fetch_carbon_forecast(fetcher)
        validate_carbon_curve(curve)
        if store is not None:
            store.record(
                DataFreshness(
                    run_id=run_id, source="carbon_intensity",
                    fetched_at=datetime.now(UTC).isoformat(timespec="seconds"),
                    expected_slots=SLOTS_PER_DAY, actual_slots=len(curve),
                    is_fresh=len(curve) >= SLOTS_PER_DAY,
                )
            )
        slots = build_planning_slots(curve, config.tariff)
        schedule = optimise(
            config.tasks, slots, config.objective, config.weights,
            using_actual_carbon=config.using_actual_carbon,
            tariff_is_manual=getattr(config.tariff, "is_manual", True),
        )
    except Exception as exc:  # noqa: BLE001 - degrade gracefully, never crash the job
        fallback = last_good.load() if last_good is not None else None
        if fallback is not None:
            _record_run("fallback", 0, f"{type(exc).__name__}: {exc}; used last good schedule")
            return PipelineResult(run_id, "fallback", fallback, str(exc))
        _record_run("failed", 0, f"{type(exc).__name__}: {exc}")
        return PipelineResult(run_id, "failed", None, str(exc))

    if last_good is not None:
        last_good.save(schedule)
    if store is not None:
        store.record(
            OptimisationQuality(
                run_id=run_id, objective=str(config.objective),
                task_count=len(schedule.tasks),
                total_cost_saving_p=round(schedule.total_cost_saving_p, 3),
                total_carbon_saving_g=round(schedule.total_carbon_saving_g, 3),
                avg_robustness=round(average_robustness(schedule), 3),
                constraint_violations=constraint_violations(config.tasks, schedule),
            )
        )
    _record_run("success", len(curve), "")
    return PipelineResult(run_id, "success", schedule, "")
