"""Quality metrics over a :class:`Schedule`, shared by the pipeline's monitoring
and the optimiser-comparison experiment so the two never drift."""

from __future__ import annotations

from community_energy_flex.domain.models import Schedule, Task


def constraint_violations(tasks: list[Task], schedule: Schedule) -> int:
    """Count scheduled tasks that fall outside their own feasible window."""
    by_id = {t.task_id: t for t in tasks}
    return sum(
        1
        for st in schedule.tasks
        if st.start_index < by_id[st.task_id].earliest_start
        or st.end_index > by_id[st.task_id].latest_finish
    )


def average_robustness(schedule: Schedule) -> float:
    if not schedule.tasks:
        return 0.0
    return sum(t.robustness_score for t in schedule.tasks) / len(schedule.tasks)
