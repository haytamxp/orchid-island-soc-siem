from __future__ import annotations

import csv
from pathlib import Path

import pytest

from backend.ml.benchmark import (
    run_benchmark,
)
from backend.ml.robustness import (
    BenchmarkResult,
    compare_results,
)


def test_compare_results_uses_first_result_as_baseline() -> None:
    baseline = BenchmarkResult(
        name="baseline",
        samples=100,
        malicious_rate=0.2,
        precision=0.95,
        recall=0.90,
        f1=0.925,
        pr_auc=0.96,
        roc_auc=0.97,
        false_positive_rate=0.01,
        false_negative_rate=0.10,
        threshold=0.45,
    )

    shifted = BenchmarkResult(
        name="shifted",
        samples=100,
        malicious_rate=0.2,
        precision=0.90,
        recall=0.80,
        f1=0.847,
        pr_auc=0.89,
        roc_auc=0.92,
        false_positive_rate=0.02,
        false_negative_rate=0.20,
        threshold=0.45,
    )

    report = compare_results(
        [
            baseline,
            shifted,
        ]
    )

    assert report[
        "baseline"
    ]["name"] == "baseline"

    assert (
        report["results"][1][
            "delta_f1"
        ]
        == pytest.approx(
            shifted.f1
            - baseline.f1
        )
    )


def test_compare_results_rejects_empty() -> None:
    with pytest.raises(
        ValueError
    ):
        compare_results([])


def test_benchmark_requires_valid_model_path() -> None:
    with pytest.raises(
        FileNotFoundError
    ):
        run_benchmark(
            model_path=(
                "models/"
                "does-not-exist.joblib"
            ),
            datasets={
                "baseline": (
                    "database/"
                    "missing.csv"
                )
            },
        )
