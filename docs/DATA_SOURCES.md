# Data sources and provenance

The API reports the source actually used for each response. Regional capability and response-level provenance are separate: `supports_live_forecast` says whether live coverage is supported, while `is_live_forecast` says what happened for this request.

## Carbon

| Source id | Label | Live? | Use |
|---|---|---:|---|
| `gb_live_forecast` | GB Carbon Intensity forecast | yes | GB forecast requests when the provider returns a valid curve |
| `ni_eirgrid_typical_profile` | Northern Ireland EirGrid-derived typical profile | no | Northern Ireland planning |
| `gb_sample_profile` | GB sample carbon profile | no | Safe fallback when the GB provider times out, fails, or returns invalid data |
| `unavailable` | Carbon data unavailable | no | Reserved explicit unavailable state |

The GB source is the public Carbon Intensity API operated by NESO with academic partners. Retrieval and valid-period timestamps are retained when supplied. Provider errors are converted into typed fallback reasons; raw exception strings are not exposed to clients.

Typical and sample profiles are planning aids, not forecasts of the requested day.

## Prices

The public workflow supports user-entered flat and Economy 7 tariffs plus Octopus Agile retrieval for configured GB regions. User-entered responses use `price_source = user_entered_tariff` and `price_is_live = false`; successfully retrieved Agile rates use `price_source = octopus_agile_live` and `price_is_live = true`. Forecast responses distinguish `not_supported` from `not_published` when no price curve is returned.

Python callers can also build a `MultiBandTariff` from 48 supplied half-hourly values. Standing charges are retained in the tariff model but excluded from shift savings because moving a task does not change them.

## Task constraints

Tasks are user-entered. The public API validates positive energy and duration, caps energy at 500 kWh and duration at 24 hours, limits a request to 50 tasks, and checks that each task fits its allowed window.

Core fields are defined in `src/community_energy_flex/domain/models.py`; HTTP request limits are defined in `api/community_energy_api/models.py`.
