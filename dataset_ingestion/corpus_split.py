"""
Temporal splitting utilities for UNSW-NB15.

The split is based on event time, not random shuffling.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def temporal_boundaries(
    dataset_path: str | Path,
    train_ratio: float = 0.70,
    validation_ratio: float = 0.15,
) -> tuple[int, int]:
    if not (
        0.0 < train_ratio < 1.0
    ):
        raise ValueError(
            "train_ratio must be between 0 and 1"
        )

    if not (
        0.0 < validation_ratio < 1.0
    ):
        raise ValueError(
            "validation_ratio must be between 0 and 1"
        )

    if train_ratio + validation_ratio >= 1.0:
        raise ValueError(
            "train_ratio + validation_ratio must be < 1"
        )

    timestamps: list[np.ndarray] = []

    for chunk in pd.read_csv(
        Path(dataset_path),
        usecols=["stime"],
        chunksize=200_000,
    ):
        values = pd.to_numeric(
            chunk["stime"],
            errors="coerce",
        ).dropna().to_numpy(
            dtype=np.int64
        )

        if values.size:
            timestamps.append(values)

    if not timestamps:
        raise ValueError(
            "No valid timestamps found"
        )

    all_timestamps = np.concatenate(
        timestamps
    )

    train_cut = int(
        np.quantile(
            all_timestamps,
            train_ratio,
        )
    )

    validation_cut = int(
        np.quantile(
            all_timestamps,
            train_ratio + validation_ratio,
        )
    )

    if validation_cut <= train_cut:
        raise ValueError(
            "Temporal boundaries collapsed; "
            "timestamp distribution is insufficient"
        )

    return train_cut, validation_cut


def assign_temporal_split(
    timestamps: pd.Series,
    train_cut: int,
    validation_cut: int,
) -> pd.Series:
    values = pd.to_numeric(
        timestamps,
        errors="coerce",
    ).fillna(train_cut)

    return pd.Series(
        np.where(
            values <= train_cut,
            "train",
            np.where(
                values <= validation_cut,
                "validation",
                "test",
            ),
        ),
        index=timestamps.index,
    )
