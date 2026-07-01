from __future__ import annotations

import pytest

from community_energy_flex.data_sources.tariffs import FlatTariff
from community_energy_flex.demo import sample_carbon_curve, sample_tasks
from community_energy_flex.domain.models import Objective
from community_energy_flex.experiments.optimiser_comparison import compare_optimisers
from community_energy_flex.optimisation.planning import build_planning_slots

pytest.importorskip("pulp")


def _slots():
    return build_planning_slots(sample_carbon_curve(), FlatTariff(unit_rate_p=28.0))


def test_compares_both_optimisers_for_each_objective():
    objectives = [Objective.CHEAPEST, Objective.LOWEST_CARBON]
    results = compare_optimisers(sample_tasks(), _slots(), objectives)
    assert len(results) == 2 * len(objectives)
    assert {r.optimiser for r in results} == {"rule_based", "lp"}


def test_no_optimiser_violates_constraints_and_runtime_recorded():
    results = compare_optimisers(sample_tasks(), _slots())
    assert all(r.constraint_violations == 0 for r in results)
    assert all(r.runtime_s >= 0 for r in results)


def test_lp_respects_peak_cap_that_couples_tasks():
    # A cap that bites should still yield a valid (0-violation) LP schedule.
    results = compare_optimisers(
        sample_tasks(), _slots(), [Objective.CHEAPEST], max_load_kw=5.0
    )
    lp = next(r for r in results if r.optimiser == "lp")
    assert lp.constraint_violations == 0
