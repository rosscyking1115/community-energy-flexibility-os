"""Carbon-curve provider for the API.

- GB regions: live 24h regional forecast from the Carbon Intensity API.
- Northern Ireland: the precomputed EirGrid typical-day profile (no live
  forecast exists for NI).
- Any failure degrades gracefully to the sample curve, so a feed outage never
  takes the API down. Results are cached per region with a TTL.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from community_energy_flex.data_sources.carbon_intensity import (
    CarbonIntensityClient,
    carbon_curve,
)
from community_energy_flex.demo import sample_carbon_curve

_TTL_SECONDS = 1800
_NI_PROFILE = Path(__file__).resolve().parents[2] / "data" / "reference" / "ni_carbon_profile.json"
_cache: dict[str, tuple[float, list[float], str]] = {}


def _gb_curve(region: dict, client: CarbonIntensityClient | None = None) -> tuple[list[float], str]:
    client = client or CarbonIntensityClient()
    slots = client.regional_forecast_by_id(region["carbon_region_id"])
    return carbon_curve(slots), "live_forecast"


def _ni_curve(region: dict) -> tuple[list[float], str]:
    data = json.loads(_NI_PROFILE.read_text(encoding="utf-8"))
    return list(data["curve"]), "typical_profile"


def provider(region: dict) -> tuple[list[float], str]:
    """Return (48-slot carbon curve, source) for a region, cached with a TTL."""
    key = region["id"]
    now = time.monotonic()
    cached = _cache.get(key)
    if cached and cached[0] > now:
        return cached[1], cached[2]
    try:
        source_kind = region["carbon_source"]
        if source_kind == "gb_carbon_intensity":
            curve, source = _gb_curve(region)
        elif source_kind == "eirgrid_ni":
            curve, source = _ni_curve(region)
        else:
            curve, source = sample_carbon_curve(), "sample"
    except Exception:  # noqa: BLE001 - a feed outage must never break the API
        curve, source = sample_carbon_curve(), "sample"
    _cache[key] = (now + _TTL_SECONDS, curve, source)
    return curve, source


def clear_cache() -> None:
    _cache.clear()
