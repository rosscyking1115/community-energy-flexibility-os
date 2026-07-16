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
    result = carbon._gb_curve(region, client=client)
    assert result.source == "gb_live_forecast"
    assert result.is_live_forecast is True
    assert result.is_fallback is False
    assert len(result.values) == 48 and result.values[0] == 100


def test_ni_region_uses_typical_profile():
    region = {"id": "northern-ireland", "carbon_source": "eirgrid_ni", "carbon_region_id": None}
    result = carbon._ni_curve(region)
    assert result.source == "ni_eirgrid_typical_profile"
    assert "EirGrid" in result.source_label
    assert result.is_live_forecast is False
    assert len(result.values) == 48


def test_provider_falls_back_to_gb_sample_on_timeout(monkeypatch):
    carbon.clear_cache()
    monkeypatch.setattr(
        carbon, "_gb_curve", lambda r: (_ for _ in ()).throw(TimeoutError("secret detail"))
    )
    region = {"id": "london", "carbon_source": "gb_carbon_intensity", "carbon_region_id": 13}
    result = carbon.provider(region)
    assert result.source == "gb_sample_profile"
    assert result.source_label == "GB sample profile"
    assert result.is_fallback is True
    assert result.fallback_reason == "upstream_timeout"
    assert "secret detail" not in repr(result)
    assert len(result.values) == 48


def test_provider_classifies_invalid_payload_and_cache_preserves_provenance(monkeypatch):
    carbon.clear_cache()
    calls = 0

    def fail(_region):
        nonlocal calls
        calls += 1
        raise ValueError("bad upstream shape")

    monkeypatch.setattr(carbon, "_gb_curve", fail)
    region = {"id": "london", "carbon_source": "gb_carbon_intensity", "carbon_region_id": 13}
    first = carbon.provider(region)
    second = carbon.provider(region)
    assert first is second
    assert calls == 1
    assert second.fallback_reason == "invalid_payload"


def test_ni_profile_failure_never_falls_back_to_gb_data(monkeypatch):
    carbon.clear_cache()
    monkeypatch.setattr(
        carbon, "_ni_curve", lambda r: (_ for _ in ()).throw(ValueError("bad NI profile"))
    )
    region = {
        "id": "northern-ireland",
        "carbon_source": "eirgrid_ni",
        "carbon_region_id": None,
    }

    result = carbon.provider(region)

    assert result.source == "unavailable"
    assert result.source_label == "Carbon data unavailable"
    assert result.values == []
    assert result.is_fallback is True
    assert result.fallback_reason == "invalid_payload"
