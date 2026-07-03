"""Keep API tests offline: stub the carbon provider so /v1/optimise never hits
the live carbon feed during tests."""

from __future__ import annotations

import pytest

pytest.importorskip("fastapi")

import community_energy_api.main as main  # noqa: E402
from community_energy_flex.demo import sample_carbon_curve  # noqa: E402


@pytest.fixture(autouse=True)
def offline_carbon(monkeypatch):
    monkeypatch.setattr(main, "carbon_provider", lambda region: (sample_carbon_curve(), "sample"))
