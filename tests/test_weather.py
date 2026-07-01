from __future__ import annotations

from community_energy_flex.data_sources.weather import (
    WeatherClient,
    cloud_cover_slots,
    parse_hourly,
    temperature_slots,
)

PAYLOAD = {
    "hourly": {
        "time": ["2026-07-01T00:00", "2026-07-01T01:00"],
        "temperature_2m": [15.0, 16.0],
        "cloud_cover": [50, 80],
        "wind_speed_10m": [10, 12],
    }
}


def test_parses_hourly_records():
    hours = parse_hourly(PAYLOAD)
    assert len(hours) == 2
    assert hours[0].temperature_c == 15.0
    assert hours[1].cloud_cover_pct == 80


def test_hourly_expands_to_half_hour_slots():
    hours = parse_hourly(PAYLOAD)
    assert temperature_slots(hours, num_slots=4) == [15.0, 15.0, 16.0, 16.0]
    assert cloud_cover_slots(hours, num_slots=4) == [50, 50, 80, 80]


def test_slot_expansion_pads_when_short():
    hours = parse_hourly(PAYLOAD)
    # only 2 hours -> 4 slots of data; request 6 -> last value padded
    assert temperature_slots(hours, num_slots=6) == [15.0, 15.0, 16.0, 16.0, 16.0, 16.0]


def test_client_uses_injected_fetch():
    client = WeatherClient(fetch=lambda url: PAYLOAD)
    hours = client.hourly_forecast(51.45, -2.58)
    assert len(hours) == 2
