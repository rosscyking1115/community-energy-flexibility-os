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
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from community_energy_flex.data_sources.carbon_intensity import (
    CarbonIntensityClient,
    carbon_curve,
)
from community_energy_flex.demo import sample_carbon_curve

_TTL_SECONDS = 1800
_NI_PROFILE = Path(__file__).resolve().parents[2] / "data" / "reference" / "ni_carbon_profile.json"
CarbonSource = Literal[
    "gb_live_forecast",
    "ni_eirgrid_typical_profile",
    "gb_sample_profile",
    "unavailable",
]
FallbackReason = Literal[
    "upstream_timeout",
    "upstream_error",
    "invalid_payload",
    "unsupported_source",
]


@dataclass(frozen=True)
class CarbonCurveResult:
    values: list[float]
    source: CarbonSource
    source_label: str
    retrieved_at_utc: datetime | None = None
    valid_from_utc: datetime | None = None
    valid_to_utc: datetime | None = None
    is_fallback: bool = False
    fallback_reason: FallbackReason | None = None

    @property
    def is_live_forecast(self) -> bool:
        return self.source == "gb_live_forecast"


_cache: dict[str, tuple[float, CarbonCurveResult]] = {}


def _gb_curve(
    region: dict, client: CarbonIntensityClient | None = None
) -> CarbonCurveResult:
    client = client or CarbonIntensityClient()
    slots = client.regional_forecast_by_id(region["carbon_region_id"])
    return CarbonCurveResult(
        values=carbon_curve(slots),
        source="gb_live_forecast",
        source_label="NESO / Carbon Intensity regional forecast",
        retrieved_at_utc=datetime.now(UTC),
        valid_from_utc=slots[0].start if slots else None,
        valid_to_utc=slots[-1].end if slots else None,
    )


def _ni_curve(region: dict) -> CarbonCurveResult:
    data = json.loads(_NI_PROFILE.read_text(encoding="utf-8"))
    return CarbonCurveResult(
        values=list(data["curve"]),
        source="ni_eirgrid_typical_profile",
        source_label="EirGrid Northern Ireland typical-day profile",
    )


def _fallback_reason(exc: Exception) -> FallbackReason:
    if isinstance(exc, TimeoutError):
        return "upstream_timeout"
    if isinstance(exc, (json.JSONDecodeError, KeyError, TypeError, ValueError)):
        return "invalid_payload"
    return "upstream_error"


def _sample_result(reason: FallbackReason) -> CarbonCurveResult:
    return CarbonCurveResult(
        values=sample_carbon_curve(),
        source="gb_sample_profile",
        source_label="GB sample profile",
        is_fallback=True,
        fallback_reason=reason,
    )


def _unavailable_result(reason: FallbackReason) -> CarbonCurveResult:
    return CarbonCurveResult(
        values=[],
        source="unavailable",
        source_label="Carbon data unavailable",
        is_fallback=True,
        fallback_reason=reason,
    )


def provider(region: dict) -> CarbonCurveResult:
    """Return a 48-slot curve with provenance, cached without losing identity."""
    key = region["id"]
    now = time.monotonic()
    cached = _cache.get(key)
    if cached and cached[0] > now:
        return cached[1]
    source_kind = region.get("carbon_source")
    try:
        if source_kind == "gb_carbon_intensity":
            result = _gb_curve(region)
        elif source_kind == "eirgrid_ni":
            result = _ni_curve(region)
        else:
            result = _unavailable_result("unsupported_source")
    except Exception as exc:  # noqa: BLE001 - safe, typed fallback is intentional
        reason = _fallback_reason(exc)
        result = (
            _sample_result(reason)
            if source_kind == "gb_carbon_intensity"
            else _unavailable_result(reason)
        )
    _cache[key] = (now + _TTL_SECONDS, result)
    return result


def clear_cache() -> None:
    _cache.clear()
