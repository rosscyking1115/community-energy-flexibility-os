"""Client for the Open-Meteo weather API (free, no key).

Weather is a feature for the demand forecast (heating/cooling proxy) and a solar
estimate (cloud cover). Open-Meteo returns hourly values; we expand them to the
48 half-hour planning slots. Parsing is separated from I/O for network-free
tests.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from community_energy_flex.domain.models import SLOTS_PER_DAY

BASE_URL = "https://api.open-meteo.com/v1/forecast"
_USER_AGENT = "community-energy-flexibility-os/0.1 (+https://github.com)"
_HOURLY_VARS = ("temperature_2m", "cloud_cover", "wind_speed_10m")


@dataclass(frozen=True)
class WeatherHour:
    time: str
    temperature_c: float | None
    cloud_cover_pct: float | None
    wind_speed_kmh: float | None


def parse_hourly(payload: dict) -> list[WeatherHour]:
    hourly = payload.get("hourly", {})
    times = hourly.get("time", [])
    temp = hourly.get("temperature_2m", [])
    cloud = hourly.get("cloud_cover", [])
    wind = hourly.get("wind_speed_10m", [])

    def _at(seq, i):
        return seq[i] if i < len(seq) else None

    return [
        WeatherHour(
            time=t,
            temperature_c=_at(temp, i),
            cloud_cover_pct=_at(cloud, i),
            wind_speed_kmh=_at(wind, i),
        )
        for i, t in enumerate(times)
    ]


def _to_slots(hourly_values: list[float | None], num_slots: int) -> list[float | None]:
    """Expand hourly values to half-hour slots by repeating each hour twice."""
    slots: list[float | None] = []
    for v in hourly_values:
        slots.extend([v, v])
    if len(slots) < num_slots:
        slots.extend([slots[-1] if slots else None] * (num_slots - len(slots)))
    return slots[:num_slots]


def temperature_slots(
    hours: list[WeatherHour], num_slots: int = SLOTS_PER_DAY
) -> list[float | None]:
    return _to_slots([h.temperature_c for h in hours], num_slots)


def cloud_cover_slots(
    hours: list[WeatherHour], num_slots: int = SLOTS_PER_DAY
) -> list[float | None]:
    return _to_slots([h.cloud_cover_pct for h in hours], num_slots)


class WeatherClient:
    """Thin HTTP client. Inject ``fetch`` to test without a network."""

    def __init__(self, base_url: str = BASE_URL, fetch=None) -> None:
        self.base_url = base_url
        self._fetch = fetch or self._http_get

    def _http_get(self, url: str) -> dict:
        req = Request(url, headers={"Accept": "application/json", "User-Agent": _USER_AGENT})
        with urlopen(req, timeout=20) as resp:  # noqa: S310 - fixed https host
            return json.loads(resp.read().decode("utf-8"))

    def hourly_forecast(self, latitude: float, longitude: float) -> list[WeatherHour]:
        query = urlencode(
            {
                "latitude": latitude,
                "longitude": longitude,
                "hourly": ",".join(_HOURLY_VARS),
                "forecast_days": 2,
            }
        )
        return parse_hourly(self._fetch(f"{self.base_url}?{query}"))
