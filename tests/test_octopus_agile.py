from __future__ import annotations

from datetime import date

from community_energy_flex.data_sources.octopus_agile import (
    OctopusAgileClient,
    agile_tariff_for_day,
    day_price_curve,
    parse_agile_rates,
)


def _rate(hh_from: str, hh_to: str, price: float) -> dict:
    return {
        "valid_from": f"2026-07-01T{hh_from}:00Z",
        "valid_to": f"2026-07-01T{hh_to}:00Z",
        "value_inc_vat": price,
    }


# API returns newest-first; note the deliberately unsorted order here.
PAYLOAD = {
    "results": [
        _rate("01:00", "01:30", 12.0),
        _rate("00:00", "00:30", 10.0),
        _rate("00:30", "01:00", 8.0),
    ]
}


def test_rates_are_parsed_and_sorted_oldest_first():
    rates = parse_agile_rates(PAYLOAD)
    assert [r.price_p for r in rates] == [10.0, 8.0, 12.0]


def test_day_price_curve_carries_missing_slots_forward():
    rates = parse_agile_rates(PAYLOAD)
    curve = day_price_curve(rates, date(2026, 7, 1), num_slots=4)
    # slots 0..2 present; slot 3 (01:30) missing -> carries 12.0 forward
    assert curve == [10.0, 8.0, 12.0, 12.0]


def test_agile_tariff_is_slot_aligned_and_not_manual():
    rates = parse_agile_rates(PAYLOAD)
    tariff = agile_tariff_for_day(rates, date(2026, 7, 1))
    assert tariff.unit_rate_p_per_kwh(0) == 10.0
    assert tariff.unit_rate_p_per_kwh(1) == 8.0
    assert tariff.unit_rate_p_per_kwh(47) == 12.0  # carried forward
    assert tariff.is_manual is False


def test_client_builds_the_expected_url():
    seen = {}

    def fake_fetch(url):
        seen["url"] = url
        return PAYLOAD

    client = OctopusAgileClient(fetch=fake_fetch)
    client.unit_rates("AGILE-24-04-03", "E-1R-AGILE-24-04-03-C")
    assert "products/AGILE-24-04-03/electricity-tariffs/E-1R-AGILE-24-04-03-C" in seen["url"]
    assert seen["url"].endswith("/standard-unit-rates/")
