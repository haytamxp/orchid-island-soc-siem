"""
Compare V2 and V3 model metrics.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_metrics(
    path: str | Path,
) -> dict[str, Any]:
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Metrics file not found: {file_path}"
        )

    return json.loads(
        file_path.read_text(
            encoding="utf-8"
        )
    )


def compare(
    v2_path: str | Path,
    v3_path: str | Path,
) -> dict[str, Any]:
    v2 = load_metrics(v2_path)
    v3 = load_metrics(v3_path)

    v2_test = v2["test"]
    v3_test = v3["test"]

    metrics = [
        "precision",
        "recall",
        "f1",
        "pr_auc",
        "roc_auc",
        "false_positive_rate",
        "false_negative_rate",
    ]

    comparison = {}

    for metric in metrics:
        comparison[metric] = {
            "v2": v2_test[metric],
            "v3": v3_test[metric],
            "delta": (
                v3_test[metric]
                - v2_test[metric]
            ),
        }

    return {
        "v2_version": v2.get(
            "version",
            "unknown",
        ),
        "v3_version": v3.get(
            "version",
            "unknown",
        ),
        "comparison": comparison,
    }


def print_comparison(
    report: dict[str, Any],
) -> None:
    print("")
    print(
        "=== V2 vs V3 ==="
    )
    print("")

    print(
        "Metric".ljust(25),
        "V2".rjust(10),
        "V3".rjust(10),
        "Delta".rjust(10),
    )

    print("-" * 60)

    for metric, values in report[
        "comparison"
    ].items():
        print(
            metric.ljust(25),
            f"{values['v2']:.4f}".rjust(10),
            f"{values['v3']:.4f}".rjust(10),
            f"{values['delta']:+.4f}".rjust(10),
        )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--v2",
        required=True,
    )

    parser.add_argument(
        "--v3",
        required=True,
    )

    args = parser.parse_args()

    report = compare(
        args.v2,
        args.v3,
    )

    print_comparison(
        report
    )
