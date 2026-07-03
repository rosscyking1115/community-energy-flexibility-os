from __future__ import annotations

import pytest

pytest.importorskip("fastapi")

from community_energy_api import carbon  # noqa: E402
from community_energy_flex.data_sources.carbon_intensity import CarbonIntensityClient  # noqa: E402


def _periods(n: int = 48) -> list[dict]:
    out = []
    for i in range(n):
        hh, mm = i // 2, "30" if i % 2 else "00"
        stamp = f"2026-07-03T{hh:02d}:{mm}Z"
        out.append({"from": stamp, "to": stamp, "intensity": {"forecast": 100 + i, "actual": None}})
    return out


FORECAST = {"data": {"regionid": 13, "data": _periods()}}


def test_gb_region_uses_live_forecast():
    region = {"id": "london", "carbon_source": "gb_carbon_intensity", "carbon_region_id": 13}
    client = CarbonIntensityClient(fetch=lambda url: FORECAST)
    curve, source = carbon._gb_curve(region, client=client)
    assert source == "live_forecast"
    assert len(curve) == 48 and curve[0] == 100


def test_ni_region_uses_typical_profile():
    region = {"id": "northern-ireland", "carbon_source": "eirgrid_ni", "carbon_region_id": None}
    curve, source = carbon._ni_curve(region)
    assert source == "typical_profile"
    assert len(curve) == 48


def test_provider_falls_back_to_sample_on_feed_failure(monkeypatch):
    carbon.clear_cache()
    monkeypatch.setattr(
        carbon, "_gb_curve", lambda r: (_ for _ in ()).throw(RuntimeError("feed down"))
    )
    region = {"id": "london", "carbon_source": "gb_carbon_intensity", "carbon_region_id": 13}
    curve, source = carbon.provider(region)
    assert source == "sample" and len(curve) == 48
