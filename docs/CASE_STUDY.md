# Worked example: synthetic household

This example illustrates the decision flow using generated household tasks, a sample half-hourly carbon curve, and an example tariff. The numbers are demonstration outputs, not measured customer savings.

## Decision

The household supplies three flexible tasks, their energy and duration, allowed windows, and preferred starts. The engine constructs feasible half-hour starts, evaluates cost and carbon, and recommends a schedule for the selected objective.

Each result includes:

- the recommended and baseline windows;
- estimated cost and carbon difference relative to the preferred-start baseline;
- a robustness band and caveat;
- the carbon and price source labels.

The baseline is explicit but limited: it represents the entered preferred start, not a statistically estimated counterfactual.

## Stress test

`scripts/retro_demo.py` applies deterministic synthetic changes to the carbon curve and recomputes both windows. The resulting conditional ex-post savings show how the comparison changes if the schedule and task load shape are held fixed.

Schedule adherence is not observed, so the stress test cannot establish household outcomes. It is evidence that the calculation behaves coherently under controlled scenarios, not evidence of operational savings.

## Stakeholder reporting

The same synthetic dataset feeds the Power BI example so technical and stakeholder views can be compared. Dashboard KPIs remain illustrative and carry the same evidence boundary.

## Reproduce

```bash
python scripts/case_study.py
python scripts/retro_demo.py
python scripts/generate_powerbi_seed.py
```

See [METHODOLOGY.md](METHODOLOGY.md), [DATA_SOURCES.md](DATA_SOURCES.md), and [CLAIM_LEDGER.md](CLAIM_LEDGER.md).
