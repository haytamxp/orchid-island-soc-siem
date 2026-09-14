"""
UNSW-NB15 dataset statistics.

Produces reproducible corpus statistics without loading the complete
dataset into memory.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import pandas as pd


def analyze(
    dataset_path: str | Path,
    chunk_size: int = 100_000,
) -> dict:
    path = Path(dataset_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {path}"
        )

    total = 0
    labels = Counter()
    attacks = Counter()
    missingness = Counter()

    minimum_time = None
    maximum_time = None

    for chunk in pd.read_csv(
        path,
        chunksize=chunk_size,
    ):
        total += len(chunk)

        labels.update(
            chunk["label"]
            .fillna(-1)
            .astype(int)
            .tolist()
        )

        if "attack_cat" in chunk.columns:
            normalized = (
                chunk["attack_cat"]
                .fillna("__MISSING__")
                .astype(str)
            )
            attacks.update(
                normalized.tolist()
            )

        for column in chunk.columns:
            missingness[column] += int(
                chunk[column].isna().sum()
            )

        times = pd.to_numeric(
            chunk["stime"],
            errors="coerce",
        ).dropna()

        if not times.empty:
            local_min = int(times.min())
            local_max = int(times.max())

            minimum_time = (
                local_min
                if minimum_time is None
                else min(minimum_time, local_min)
            )

            maximum_time = (
                local_max
                if maximum_time is None
                else max(maximum_time, local_max)
            )

    result = {
        "dataset": str(path),
        "rows": total,
        "labels": {
            str(k): int(v)
            for k, v in sorted(labels.items())
        },
        "attack_categories": {
            str(k): int(v)
            for k, v in sorted(attacks.items())
        },
        "missing_values": {
            str(k): int(v)
            for k, v in sorted(missingness.items())
            if v
        },
        "minimum_stime": minimum_time,
        "maximum_stime": maximum_time,
        "malicious_rate": (
            labels.get(1, 0) / total
            if total
            else 0.0
        ),
    }

    print(
        json.dumps(
            result,
            indent=2,
        )
    )

    return result


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--dataset",
        default=(
            "data/processed/unsw_nb15/"
            "unsw_nb15_clean.csv"
        ),
    )

    args = parser.parse_args()

    analyze(args.dataset)


if __name__ == "__main__":
    main()
