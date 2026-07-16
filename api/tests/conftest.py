"""Keep API tests offline: stub the carbon provider so /v1/optimise never hits
the live carbon feed during tests."""

from __future__ import annotations

import pytest

pytest.importorskip("fastapi")

import community_energy_api.main as main  # noqa: E402
from community_energy_api.carbon import CarbonCurveResult  # noqa: E402
from community_energy_flex.demo import sample_carbon_curve  # noqa: E402


@pytest.fixture(autouse=True)
def offline_feeds(monkeypatch):
    from community_energy_api.agile import AgileUnavailable

    def _fake_carbon(region):
        if region["carbon_source"] == "eirgrid_ni":
            return CarbonCurveResult(
                values=sample_carbon_curve(),
                source="ni_eirgrid_typical_profile",
                source_label="EirGrid Northern Ireland typical-day profile",
            )
        return CarbonCurveResult(
            values=sample_carbon_curve(),
            source="gb_sample_profile",
            source_label="GB sample profile",
            is_fallback=True,
            fallback_reason="upstream_error",
        )

    monkeypatch.setattr(main, "carbon_provider", _fake_carbon)

    def _fake_agile(region):
        if region.get("agile_gsp") is None:
            raise AgileUnavailable(f"Agile is not available in {region['name']}")
        return [15.0] * 48, "2026-07-04"

    monkeypatch.setattr(main, "agile_provider", _fake_agile)
