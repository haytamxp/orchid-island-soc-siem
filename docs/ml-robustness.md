# Orchid Island ML Robustness Evaluation

## Objective

The behavioral detector must be evaluated against changes that commonly
occur when a model moves from synthetic data into a real SOC.

A strong benchmark should not only measure baseline performance. It should
also measure performance when semantic and contextual signals change.

## Stress scenarios

### Baseline

The original chronological test set.

### Semantic blind

Descriptions are replaced with generic text and categories are normalized.

Purpose:

- detect dependence on attack terminology
- expose semantic shortcut learning
- verify that behavior features still carry predictive value

### Severity shift

Severity values are downgraded.

Purpose:

- test whether the model is over-dependent on collector severity
- simulate inconsistent sensor configuration

### Source shift

Wazuh, Suricata, web, and Cloudflare source labels are remapped.

Purpose:

- simulate sensor migration
- test cross-source generalization

### Combined shift

Semantic information, severity, and source identity are all modified.

Purpose:

- approximate a substantially different telemetry distribution

## Metrics

The benchmark records:

- Precision
- Recall
- F1
- PR-AUC
- ROC-AUC
- False Positive Rate
- False Negative Rate

PR-AUC is particularly important for imbalanced security datasets because
precision and recall describe positive-class performance more directly than
plain accuracy.

## Interpretation

Do not optimize for one metric in isolation.

A healthy detector should maintain:

- high recall for genuine attacks
- high precision to limit analyst fatigue
- low false-positive rate
- stable performance under reasonable distribution shifts

A large performance collapse under `semantic_blind` indicates the model may
have depended on textual clues.

A large collapse under `severity_shift` indicates excessive dependence on
upstream severity labeling.

A large collapse under `source_shift` indicates collector-specific bias.

A large collapse under `combined_shift` indicates poor generalization and
requires additional real-world training data or more robust feature design.

## Current benchmark boundary

This benchmark is still synthetic. Passing it does not establish production
detection quality.

The next validation stage should use real security telemetry such as Wazuh,
Suricata, Cloudflare, CIC-IDS2017, UNSW-NB15, or another appropriately labeled
dataset while preserving chronological evaluation.
