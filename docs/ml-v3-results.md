# Orchid Island ML V3

## Temporal integrity fix

Batch 13 exposed a state-management issue in the behavioral engine.

An event arriving with a future timestamp must not change the historical state
used for an earlier event.

The engine now:

- filters behavior windows with `timestamp <= current_event_timestamp`
- finds the latest historical timestamp at or before the current event
- ignores future events when calculating `seconds_since_previous`
- keeps the internal history chronologically ordered

This protects both offline evaluation and online scoring.

## V3 benchmark compatibility

The robustness evaluator previously used the V2 feature pipeline for every
model.

V2 contains 48 features.

V3 contains 43 behavior-first features.

The evaluator now selects the feature pipeline from the model artifact version
and validates the feature width.

## Current V3 model results

Before the temporal-state correction, V3 reported:

- Precision: 0.9865
- Recall: 0.9562
- F1: 0.9711
- PR-AUC: 0.9749
- FPR: 0.0045
- FNR: 0.0438

Those values must be regenerated after the temporal-state correction.

## Rule

Do not compare the corrected V3 model against the old V3 artifact as if the
two were identical experiments.

The model must be retrained after this fix, then evaluated again under:

- baseline
- semantic blind
- severity shift
- source shift
- combined shift

The corrected results become the authoritative V3 benchmark.

## Production status

V2 remains the current best candidate until corrected V3 robustness results
demonstrate otherwise.

Neither model should be described as production-validated using synthetic data
alone.
