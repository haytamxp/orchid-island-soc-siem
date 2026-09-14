"""
UNSW-NB15 adapter.

Converts the cleaned UNSW corpus into the ML-ready dataset consumed by
the Orchid UNSW benchmark.

The adapter deliberately preserves only label as the target and excludes
attack_cat from the feature set.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .corpus_split import (
    temporal_boundaries,
    assign_temporal_split,
)
from .unsw_features import build_feature_frame


DEFAULT_INPUT = (
    "data/processed/unsw_nb15/"
    "unsw_nb15_clean.csv"
)

DEFAULT_OUTPUT = (
    "data/processed/unsw_nb15/"
    "unsw_ml_ready.csv"
)


def adapt(
    input_path: str | Path,
    output_path: str | Path,
    chunk_size: int = 100_000,
) -> dict[str, int | float]:
    input_file = Path(input_path)
    output_file = Path(output_path)

    if not input_file.exists():
        raise FileNotFoundError(
            f"Clean UNSW dataset not found: {input_file}"
        )

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    train_cut, validation_cut = temporal_boundaries(
        input_file
    )

    first_chunk = True

    counts = {
        "rows": 0,
        "train": 0,
        "validation": 0,
        "test": 0,
        "benign": 0,
        "malicious": 0,
    }

    for chunk in pd.read_csv(
        input_file,
        chunksize=chunk_size,
    ):
        features = build_feature_frame(
            chunk
        )

        split = assign_temporal_split(
            chunk["stime"],
            train_cut,
            validation_cut,
        )

        features.insert(
            len(features.columns) - 1,
            "split",
            split,
        )

        features.to_csv(
            output_file,
            mode="w" if first_chunk else "a",
            header=first_chunk,
            index=False,
        )

        first_chunk = False

        counts["rows"] += len(features)

        counts["train"] += int(
            (split == "train").sum()
        )

        counts["validation"] += int(
            (split == "validation").sum()
        )

        counts["test"] += int(
            (split == "test").sum()
        )

        counts["benign"] += int(
            (features["label"] == 0).sum()
        )

        counts["malicious"] += int(
            (features["label"] == 1).sum()
        )

    counts["train_ratio"] = (
        counts["train"] / counts["rows"]
        if counts["rows"]
        else 0.0
    )

    counts["validation_ratio"] = (
        counts["validation"] / counts["rows"]
        if counts["rows"]
        else 0.0
    )

    counts["test_ratio"] = (
        counts["test"] / counts["rows"]
        if counts["rows"]
        else 0.0
    )

    print("=== UNSW ML Adapter ===")
    print(f"Input: {input_file}")
    print(f"Output: {output_file}")
    print(f"Rows: {counts['rows']}")
    print(f"Train: {counts['train']}")
    print(f"Validation: {counts['validation']}")
    print(f"Test: {counts['test']}")
    print(f"Benign: {counts['benign']}")
    print(f"Malicious: {counts['malicious']}")
    print(
        "Note: attack_cat is excluded from ML features."
    )

    return counts


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input",
        default=DEFAULT_INPUT,
    )

    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
    )

    parser.add_argument(
        "--chunk-size",
        type=int,
        default=100_000,
    )

    args = parser.parse_args()

    adapt(
        args.input,
        args.output,
        args.chunk_size,
    )


if __name__ == "__main__":
    main()
