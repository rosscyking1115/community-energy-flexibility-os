"""Experiment tracking. MLflow's real job here is comparing optimiser
strategies (rule-based vs LP, across objectives) with genuine params, metrics,
and artifacts - not a synthetic demand-forecast model. It joins once there is
something worth comparing; that is now."""

from community_energy_flex.experiments.optimiser_comparison import (
    ComparisonResult,
    compare_optimisers,
    log_comparison_to_mlflow,
)

__all__ = ["ComparisonResult", "compare_optimisers", "log_comparison_to_mlflow"]
