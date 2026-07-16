"""Compatibility import for the pre-0.2 robustness terminology.

New code imports :mod:`community_energy_flex.optimisation.robustness`.
"""

from community_energy_flex.optimisation.robustness import (
    RobustnessIndicator as Confidence,
)
from community_energy_flex.optimisation.robustness import compute_robustness


def compute_confidence(*args, using_actual_carbon: bool, **kwargs):
    """Deprecated wrapper retained for one pre-1.0 transition release."""
    return compute_robustness(
        *args, using_measured_carbon=using_actual_carbon, **kwargs
    )


__all__ = ["Confidence", "compute_confidence"]
