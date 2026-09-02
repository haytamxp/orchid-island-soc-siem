"""
V3 dataset pipeline.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import numpy as np

from backend.ml.behavior import BehaviorEngine
from backend.ml.behavior_features_v3 import (
    FEATURE_NAMES,
    build_behavior_features,
)
from backend.ml.schema import CanonicalEvent


@dataclass(slots=True)
class DatasetV3:
    events: list[CanonicalEvent]
    timestamps: list[object]
    features: np.ndarray
    labels: np.ndarray
    feature_names: list[str]


def load_events(
    path: str | Path,
) -> list[CanonicalEvent]:
    dataset_path = Path(path)

    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {dataset_path}"
        )

    events = []

    with dataset_path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:

        reader = csv.DictReader(
            handle
        )

        if not reader.fieldnames:
            raise ValueError(
                "Dataset has no header"
            )

        for row in reader:
            event = CanonicalEvent.from_mapping(
                row
            )

            if event.label is None:
                raise ValueError(
                    "Dataset contains an unlabeled event"
                )

            events.append(event)

    if not events:
        raise ValueError(
            "Dataset is empty"
        )

    return sorted(
        events,
        key=lambda event: event.timestamp,
    )


def build_dataset(
    events: Sequence[CanonicalEvent],
) -> DatasetV3:
    ordered = sorted(
        events,
        key=lambda event: event.timestamp,
    )

    engine = BehaviorEngine()

    rows = []
    labels = []

    for event in ordered:
        historical = engine.transform(
            event
        )

        rows.append(
            build_behavior_features(
                event,
                historical,
            )
        )

        labels.append(
            int(event.label)
        )

    matrix = np.asarray(
        rows,
        dtype=np.float32,
    )

    targets = np.asarray(
        labels,
        dtype=np.int8,
    )

    if matrix.ndim != 2:
        raise ValueError(
            "Feature matrix must be two-dimensional"
        )

    if matrix.shape[1] != len(
        FEATURE_NAMES
    ):
        raise ValueError(
            "V3 feature matrix width mismatch"
        )

    if set(
        np.unique(targets)
    ) - {0, 1}:
        raise ValueError(
            "Labels must be binary"
        )

    return DatasetV3(
        events=ordered,
        timestamps=[
            event.timestamp
            for event in ordered
        ],
        features=matrix,
        labels=targets,
        feature_names=list(
            FEATURE_NAMES
        ),
    )


def build_dataset_from_csv(
    path: str | Path,
) -> DatasetV3:
    return build_dataset(
        load_events(path)
    )
