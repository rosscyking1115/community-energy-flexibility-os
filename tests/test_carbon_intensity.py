from __future__ import annotations

from datetime import UTC, datetime

from community_energy_flex.data_sources.carbon_intensity import (
    CarbonIntensityClient,
    _next_local_midnight_utc,
    carbon_curve,
    parse_intensity_periods,
)

NATIONAL = {
    "data": [
        {"from": "2026-07-01T00:00Z", "to": "2026-07-01T00:30Z",
         "intensity": {"forecast": 120, "actual": 115}},
        {"from": "2026-07-01T00:30Z", "to": "2026-07-01T01:00Z",
         "intensity": {"forecast": 130, "actual": None}},
    ]
}

REGIONAL = {
    "data": {
        "regionid": 3, "shortname": "South West",
        "data": [
            {"from": "2026-07-01T00:00Z", "to": "2026-07-01T00:30Z",
             "intensity": {"forecast": 90, "index": "low"}},
        ],
    }
}

# The real /regional/intensity/fw24h/postcode/{outcode} response: `data` is a
# LIST of one region object whose own `data` field holds the periods.
POSTCODE = {
    "data": [
        {
            "regionid": 3, "shortname": "South West", "postcode": "BS1",
            "data": [
                {"from": "2026-07-01T00:00Z", "to": "2026-07-01T00:30Z",
                 "intensity": {"forecast": 88, "index": "low"}},
                {"from": "2026-07-01T00:30Z", "to": "2026-07-01T01:00Z",
                 "intensity": {"forecast": 92, "index": "low"}},
            ],
        }
    ]
}


def test_parses_national_periods_with_actuals():
    slots = parse_intensity_periods(NATIONAL)
    assert len(slots) == 2
    assert slots[0].best_estimate == 115  # prefers actual
    assert slots[1].best_estimate == 130  # falls back to forecast
    assert slots[0].start.tzinfo is UTC


def test_parses_nested_regional_shape():
    slots = parse_intensity_periods(REGIONAL)
    assert len(slots) == 1
    assert slots[0].forecast_gco2_per_kwh == 90


def test_parses_regional_by_postcode_list_shape():
    # data is a list wrapping one region object; periods are nested inside it.
    slots = parse_intensity_periods(POSTCODE)
    assert len(slots) == 2
    assert [s.forecast_gco2_per_kwh for s in slots] == [88, 92]


def test_client_parses_postcode_forecast():
    client = CarbonIntensityClient(fetch=lambda url: POSTCODE)
    slots = client.regional_forecast_by_postcode("BS1")
    assert len(slots) == 2


def test_regional_by_id_builds_forecast_url_with_from():
    seen = {}

    def fake(url):
        seen["url"] = url
        return REGIONAL

    client = CarbonIntensityClient(fetch=fake)
    slots = client.regional_forecast_by_id(13, datetime(2026, 7, 3, tzinfo=UTC))
    # the forward endpoint requires a {from} timestamp in the path
    assert "/regional/intensity/" in seen["url"]
    assert "/fw24h/regionid/13" in seen["url"]
    assert "T00:00Z" in seen["url"]  # next-midnight aligned
    assert len(slots) == 1


def test_next_uk_midnight_accounts_for_bst():
    now = datetime(2026, 7, 15, 12, tzinfo=UTC)

    assert _next_local_midnight_utc(now) == datetime(2026, 7, 15, 23, tzinfo=UTC)


def test_carbon_curve_pads_to_requested_length():
    slots = parse_intensity_periods(NATIONAL)
    curve = carbon_curve(slots, num_slots=4)
    assert curve == [115, 130, 130, 130]  # last value repeated


def test_client_uses_injected_fetch():
    client = CarbonIntensityClient(fetch=lambda url: NATIONAL)
    slots = client.national_forecast_48h()
    assert len(slots) == 2
