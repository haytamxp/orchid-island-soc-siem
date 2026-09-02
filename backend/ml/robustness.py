"""
Robustness evaluation helpers for the Orchid Island ML detector.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np

from backend.ml.evaluation import evaluate_binary
from backend.ml.feature_pipeline import build_dataset_from_csv
from backend.ml.model_io import load_model_artifact


@dataclass(slots=True)
class BenchmarkResult:
    name: str
    samples: int
    malicious_rate: float
    precision: float
    recall: float
    f1: float
    pr_auc: float
    roc_auc: float
    false_positive_rate: float
    false_negative_rate: float
    threshold: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def evaluate_dataset(
    model_path: str,
    dataset_path: str,
    name: str,
) -> BenchmarkResult:
    dataset = build_dataset_from_csv(
        dataset_path
    )

    artifact = load_model_artifact(
        model_path
    )

    scores = artifact.predict_proba(
        dataset.features
    )

    result = evaluate_binary(
        dataset.labels,
        scores,
        artifact.threshold,
    )

    malicious_rate = float(
        np.mean(dataset.labels == 1)
    )

    return BenchmarkResult(
        name=name,
        samples=len(dataset.labels),
        malicious_rate=malicious_rate,
        precision=result.precision,
        recall=result.recall,
        f1=result.f1,
        pr_auc=result.pr_auc,
        roc_auc=result.roc_auc,
        false_positive_rate=result.false_positive_rate,
        false_negative_rate=result.false_negative_rate,
        threshold=artifact.threshold,
    )


def compare_results(
    results: list[BenchmarkResult],
) -> dict[str, Any]:
    if not results:
        raise ValueError(
            "At least one benchmark result is required"
        )

    baseline = results[0]

    comparison = []

    for result in results:
        comparison.append(
            {
                "name": result.name,
                "precision": result.precision,
                "recall": result.recall,
                "f1": result.f1,
                "pr_auc": result.pr_auc,
                "fpr": result.false_positive_rate,
                "fnr": result.false_negative_rate,
                "delta_f1": (
                    result.f1
                    - baseline.f1
                ),
                "delta_pr_auc": (
                    result.pr_auc
                    - baseline.pr_auc
                ),
            }
        )

    return {
        "baseline": baseline.to_dict(),
        "results": comparison,
    }
