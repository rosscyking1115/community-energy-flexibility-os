# Future research

Version 0.2.0 closes the current portfolio build and freezes feature scope. The following work is intentionally deferred because it needs evidence or infrastructure beyond the demonstrator.

## Observed-outcome validation

Collect consented meter, task-execution, and forecast snapshots so schedule adherence and true ex-post outcomes can be distinguished. Define missing-data and counterfactual rules before computing any outcome metric.

## Robustness calibration

Evaluate whether the current four-factor indicator predicts recommendation stability or forecast error. Calibration would require a held-out observed dataset, a declared target event, reliability plots, and versioned thresholds.

## Forecast-vintage robustness benchmark

Preserve the planning-time forecast, later actual grid curve, source metadata, and retrieval/valid timestamps for each forecast vintage. A benchmark must separate forecast error from schedule adherence and compare the chosen window with feasible alternatives.

This work requires a new Gate 0 before implementation: name the research question, confirm dataset availability and licensing, define retention/privacy constraints, freeze evaluation splits, and state the calibration target. A latest-forecast API response is not a historical forecast-vintage dataset.

## Regional data coverage

Replace typical profiles only where a reliable, licensed, half-hourly forecast source is available. Each integration must expose timestamps, source labels, licence/attribution, and failure semantics.

## Tariff integrations

Add provider APIs only with stable contracts, caching, explicit VAT conventions, and a distinction between retrieved live prices and user-entered/sample tariffs.

## Operational evaluation

If the project moves beyond portfolio demonstration, add privacy review, authentication/authorisation, telemetry, service-level objectives, incident response, and a controlled user study.
