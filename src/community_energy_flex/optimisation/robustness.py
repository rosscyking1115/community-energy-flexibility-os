"""Deterministic robustness indicator for an optimisation recommendation.

The score is a product of four hand-designed factors in ``(0, 1]``. It is a
heuristic sensitivity signal, not a probability and not an empirically
calibrated confidence measure.
"""

from __future__ import annotations

from dataclasses import dataclass

_DECISIVE_MARGIN = 0.25
_DECISIVENESS_FLOOR = 0.3


@dataclass(frozen=True)
class RobustnessIndicator:
    value: float
    band: str
    caveat: str


def _band(value: float) -> str:
    if value >= 0.75:
        return "Strong"
    if value >= 0.5:
        return "Mixed"
    return "Fragile"


def compute_robustness(
    sorted_scores: list[float],
    *,
    horizon_hours: float,
    using_measured_carbon: bool,
    tariff_is_manual: bool,
    single_option: bool = False,
) -> RobustnessIndicator:
    """Return an uncalibrated sensitivity heuristic for a recommendation."""
    if single_option or len(sorted_scores) < 2:
        decisiveness = 0.6
    else:
        best = sorted_scores[0]
        mean = sum(sorted_scores) / len(sorted_scores)
        materiality = mean - best
        decisiveness = min(
            1.0,
            _DECISIVENESS_FLOOR
            + (1.0 - _DECISIVENESS_FLOOR) * (materiality / _DECISIVE_MARGIN),
        )

    horizon = max(0.5, 1.0 - 0.02 * max(0.0, horizon_hours - 12))
    data = 1.0 if using_measured_carbon else 0.85
    tariff = 0.8 if tariff_is_manual else 1.0

    value = max(0.0, min(1.0, decisiveness * horizon * data * tariff))
    band = _band(value)
    factors = {
        "there is little difference between the available times": decisiveness,
        "the forecast reaches far into the future": horizon,
        "carbon figures are forecast, not measured": data,
        "the tariff was entered manually": tariff,
    }
    weakest_reason = min(factors, key=factors.get)
    caveat = (
        "Robustness indicator is strong across the assessed factors."
        if band == "Strong"
        else f"Treat as indicative: {weakest_reason}."
    )
    return RobustnessIndicator(value=round(value, 3), band=band, caveat=caveat)
