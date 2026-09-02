"""
CLI entry point for ML robustness evaluation.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from backend.ml.benchmark import (
    print_report,
    run_benchmark,
)
from backend.ml.stress_dataset import (
    generate,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run Orchid Island ML robustness testing"
        )
    )

    parser.add_argument(
        "--dataset",
        required=True,
    )

    parser.add_argument(
        "--model",
        required=True,
    )

    parser.add_argument(
        "--stress-dir",
        default=(
            "database/"
            "ml_stress"
        ),
    )

    parser.add_argument(
        "--report",
        default=(
            "models/"
            "ml_robustness_report.json"
        ),
    )

    args = parser.parse_args()

    generate(
        args.dataset,
        args.stress_dir,
    )

    directory = Path(
        args.stress_dir
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
        output_path=args.report,
    )

    print_report(
        report
    )


if __name__ == "__main__":
    main()
