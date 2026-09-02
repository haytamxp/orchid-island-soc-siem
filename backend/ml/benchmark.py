"""
Benchmark orchestration for model robustness.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from backend.ml.robustness import (
    BenchmarkResult,
    compare_results,
    evaluate_dataset,
)


def run_benchmark(
    model_path: str,
    datasets: dict[str, str],
    output_path: str | None = None,
) -> dict[str, Any]:
    results: list[BenchmarkResult] = []

    for name, dataset_path in datasets.items():
        results.append(
            evaluate_dataset(
                model_path=model_path,
                dataset_path=dataset_path,
                name=name,
            )
        )

    report = compare_results(
        results
    )

    if output_path:
        output = Path(
            output_path
        )

        output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        output.write_text(
            json.dumps(
                report,
                indent=2,
            ),
            encoding="utf-8",
        )

    return report


def print_report(
    report: dict[str, Any],
) -> None:
    print("")
    print(
        "=== Orchid Island ML Robustness Benchmark ==="
    )
    print("")

    print(
        "Name".ljust(20),
        "F1".rjust(8),
        "PR-AUC".rjust(10),
        "Precision".rjust(12),
        "Recall".rjust(10),
        "FPR".rjust(10),
        "FNR".rjust(10),
    )

    print("-" * 82)

    for item in report["results"]:
        print(
            str(
                item["name"]
            ).ljust(20),
            f"{item['f1']:.4f}".rjust(8),
            f"{item['pr_auc']:.4f}".rjust(10),
            f"{item['precision']:.4f}".rjust(12),
            f"{item['recall']:.4f}".rjust(10),
            f"{item['fpr']:.4f}".rjust(10),
            f"{item['fnr']:.4f}".rjust(10),
        )

    print("")

    baseline = report["baseline"]

    print(
        "Baseline F1: "
        f"{baseline['f1']:.4f}"
    )

    print(
        "Baseline PR-AUC: "
        f"{baseline['pr_auc']:.4f}"
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "Benchmark Orchid Island ML robustness"
        )
    )

    parser.add_argument(
        "--model",
        required=True,
    )

    parser.add_argument(
        "--directory",
        default=(
            "database/"
            "ml_stress"
        ),
    )

    parser.add_argument(
        "--output",
        default=(
            "models/"
            "ml_robustness_report.json"
        ),
    )

    args = parser.parse_args()

    directory = Path(
        args.directory
    )

    datasets = {
        "baseline": str(
            directory / "baseline.csv"
        ),
        "semantic_blind": str(
            directory / "semantic_blind.csv"
        ),
        "severity_shift": str(
            directory / "severity_shift.csv"
        ),
        "source_shift": str(
            directory / "source_shift.csv"
        ),
        "combined_shift": str(
            directory / "combined_shift.csv"
        ),
    }

    report = run_benchmark(
        model_path=args.model,
        datasets=datasets,
        output_path=args.output,
    )

    print_report(
        report
    )
