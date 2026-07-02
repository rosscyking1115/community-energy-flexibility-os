# Case study: Riverside Community Centre

A worked example of the tool end to end, on a realistic community centre. Every
number here is produced by the optimiser, not hand-written — reproduce it with
`PYTHONPATH=src python scripts/case_study.py`.

## The setting

Riverside Community Centre runs a lunch club, hires out its hall, and owns a
minibus. Energy bills are rising and the trustees want to cut both cost and
carbon — but they have no budget for batteries or solar, and no smart-meter
feed yet. What they *do* have is a handful of loads that don't care exactly when
they run.

## Their flexible loads (for tomorrow)

| Load | Energy | Runs for | Constraint |
|---|---|---|---|
| Commercial dishwasher | 3.0 kWh | 1.5 h | After the lunch club, done by 22:00 |
| Water heater | 4.0 kWh | 2.0 h | Hot water ready by 08:00 |
| Minibus EV charge | 20.0 kWh | 5.0 h | Charged by 07:30 |
| Floor scrubber | 1.5 kWh | 1.0 h | Charged by 08:00 |

They're on a half-hourly (Agile-style) tariff. Today, staff just run each load
when convenient — the dishwasher straight after lunch, the heater and cleaning
kit first thing in the morning.

## What the tool recommended

Choosing the **balanced** objective (cost and carbon weighted equally):

| Load | Run at | Instead of | Saves | Confidence |
|---|---|---|---|---|
| Commercial dishwasher | 20:30–22:00 | 13:30 | 21.6p / 259 g | Medium |
| Water heater | 02:00–04:00 | 06:00 | 13.1p / 158 g | High |
| Minibus EV charge | 00:30–05:30 | 00:00 | 2.4p / 29 g | High |
| Floor scrubber | 02:30–03:30 | 06:00 | 3.8p / 46 g | High |

The moves are intuitive once you see them: hold the dishwasher until the evening
dip, and pull the morning loads back into the small hours when the grid is
cheapest and greenest — all while still meeting every deadline.

## What it's worth

| | Cost | Carbon |
|---|---|---|
| **Per day** | £0.41 | 0.49 kg CO₂ |
| **~Per month** | ~£12 | ~15 kg CO₂ |
| **~Per year** | ~£149 | ~179 kg CO₂ |

> [!NOTE]
> These are *illustrative* projections from one day, scaled — not a guarantee.
> Real days vary; the tool never claims otherwise. Even so: ~£149 and ~179 kg
> CO₂ a year, from four loads, with no new hardware and no smart meter, is a
> real result — and it scales with every extra load and participant.

## Did it actually work?

Recommendations are built on a *forecast*. The next day, the tool compares
against what the grid actually did. When the actual carbon came in ~8% dirtier
than forecast, the plan still **realised 108% of its forecast carbon saving**
(shifting away from a dirtier-than-expected peak saved even more in absolute
terms), with a forecast error of 16 gCO₂/kWh. That check — "did yesterday's plan
help?" — is what separates a real tool from a dashboard.

## What the manager sees

The community manager doesn't run the optimiser; they open the **Power BI
dashboard** ([powerbi/screenshots/community_energy_dashboard.pdf](../powerbi/screenshots/community_energy_dashboard.pdf))
and see the month's cost and carbon savings, which loads contributed most, peak
periods avoided, and how much of the saving rests on high-confidence
recommendations — aggregated, never exposing another household's detail
([RBAC_MODEL.md](RBAC_MODEL.md)).

## Honest limitations

- Savings depend on the tariff: on a flat rate, shifting time can't cut cost
  (only carbon). Time-of-use tariffs are where the money is.
- Confidence is lower far ahead and on hand-entered tariffs — shown, never hidden.
- Cross-midnight loads are modelled within a single planning day (00:00–24:00).
- The figures scale linearly here for illustration; a real rollout would measure
  actuals via the retro loop and report those instead.
