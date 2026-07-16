# Synthetic retro stress test

The retro workflow tests recommendation sensitivity by replacing the planning carbon curve with a deterministic altered curve and recomputing the scheduled and baseline windows.

It reports:

- conditional ex-post cost and carbon savings;
- forecast mean absolute error and bias;
- whether the conditional comparison remains favourable;
- `schedule_adherence_observed = false`.

This is useful for regression testing and for showing how a recommendation behaves under changed inputs. It is not a measured customer outcome: there is no smart-meter feed, execution record, or observed counterfactual.

Run the reproducible demonstration with:

```bash
python scripts/retro_demo.py
```

The scenarios and values are synthetic. A result above or below the planning estimate describes the conditional comparison under that scenario, not a percentage of savings “realised” by a household.

See [METHODOLOGY.md](METHODOLOGY.md) for the calculation boundary and [CLAIM_LEDGER.md](CLAIM_LEDGER.md) for permitted public wording.
