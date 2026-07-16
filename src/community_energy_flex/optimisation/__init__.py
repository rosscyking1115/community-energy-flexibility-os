"""Scheduling primitives, objectives, robustness, and optimiser entry points."""

from community_energy_flex.optimisation.planning import (
    DEFAULT_PEAK_SLOTS,
    build_planning_slots,
)
from community_energy_flex.optimisation.rule_based import optimise

__all__ = ["optimise", "build_planning_slots", "DEFAULT_PEAK_SLOTS"]
