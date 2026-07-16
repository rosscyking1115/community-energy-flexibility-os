from __future__ import annotations

from community_energy_flex.optimisation.robustness import compute_robustness


def _c(scores, **kw):
    defaults = dict(horizon_hours=1.0, using_measured_carbon=True, tariff_is_manual=False)
    defaults.update(kw)
    return compute_robustness(scores, **defaults)


def test_decisive_winner_has_strong_robustness():
    indicator = _c([0.0, 0.3, 0.6])
    assert indicator.band == "Strong"
    assert indicator.caveat == "Robustness indicator is strong across the assessed factors."


def test_flat_landscape_lowers_robustness():
    # When the best option barely beats the typical option, the choice is
    # low-stakes and the robustness indicator should reflect that.
    decisive = _c([0.0, 0.5, 0.5])
    flat = _c([0.0, 0.02, 0.02])
    assert flat.value < decisive.value


def test_manual_tariff_and_forecast_reduce_robustness():
    trusted = _c([0.0, 0.3], using_measured_carbon=True, tariff_is_manual=False)
    shaky = _c([0.0, 0.3], using_measured_carbon=False, tariff_is_manual=True)
    assert shaky.value < trusted.value


def test_caveat_names_the_weakest_factor():
    # Decisive choice + measured carbon, but a long horizon and a manual tariff
    # pull it out of the "High" band. The manual tariff (0.8) is the weakest
    # single factor, so it should surface as the caveat.
    indicator = _c(
        [0.0, 0.4, 0.6],
        horizon_hours=17,  # horizon factor ~0.9
        tariff_is_manual=True,  # tariff factor 0.8 (weakest)
        using_measured_carbon=True,
    )
    assert indicator.band != "Strong"
    assert "tariff" in indicator.caveat.lower()


def test_single_option_is_neither_strong_nor_weak():
    indicator = compute_robustness(
        [0.0], horizon_hours=1.0, using_measured_carbon=True,
        tariff_is_manual=False, single_option=True,
    )
    assert 0.5 <= indicator.value <= 0.75
