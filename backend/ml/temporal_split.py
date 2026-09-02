"""
Chronological train / validation / test splitting.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(slots=True)
class TemporalSplit:
    train_indices: np.ndarray
    validation_indices: np.ndarray
    test_indices: np.ndarray


def temporal_split(
    timestamps: list[object],
    train_ratio: float = 0.70,
    validation_ratio: float = 0.15,
) -> TemporalSplit:
    total = len(timestamps)

    if total < 3:
        raise ValueError(
            "At least 3 events are required"
        )

    if not 0.0 < train_ratio < 1.0:
        raise ValueError(
            "train_ratio must be between 0 and 1"
        )

    if not 0.0 <= validation_ratio < 1.0:
        raise ValueError(
            "validation_ratio must be between 0 and 1"
        )

    if (
        train_ratio + validation_ratio
        >= 1.0
    ):
        raise ValueError(
            "train_ratio + validation_ratio "
            "must be below 1"
        )

    train_end = max(
        1,
        int(total * train_ratio),
    )

    validation_end = max(
        train_end + 1,
        int(
            total
            * (
                train_ratio
                + validation_ratio
            )
        ),
    )

    if validation_end >= total:
        validation_end = total - 1

    train_indices = np.arange(
        0,
        train_end,
        dtype=np.int64,
    )

    validation_indices = np.arange(
        train_end,
        validation_end,
        dtype=np.int64,
    )

    test_indices = np.arange(
        validation_end,
        total,
        dtype=np.int64,
    )

    if (
        len(train_indices) == 0
        or len(validation_indices) == 0
        or len(test_indices) == 0
    ):
        raise ValueError(
            "Temporal split produced an empty partition"
        )

    return TemporalSplit(
        train_indices=train_indices,
        validation_indices=validation_indices,
        test_indices=test_indices,
    )
