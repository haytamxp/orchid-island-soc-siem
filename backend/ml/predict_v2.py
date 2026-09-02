"""
Inference API for the behavioral model.

The predictor accepts an event plus optional historical events.
"""

from __future__ import annotations

import json
import sys
from typing import Iterable, Mapping

import numpy as np

from backend.ml.behavior import BehaviorEngine
from backend.ml.feature_pipeline import (
    _event_features,
)
from backend.ml.model_io import (
    ModelArtifact,
    load_model_artifact,
)
from backend.ml.schema import CanonicalEvent


class BehavioralPredictor:
    def __init__(
        self,
        artifact: ModelArtifact,
    ) -> None:
        self.artifact = artifact

    def predict_event(
        self,
        event: CanonicalEvent,
        history: Iterable[CanonicalEvent] = (),
    ) -> dict:
        engine = BehaviorEngine()

        ordered_history = sorted(
            history,
            key=lambda item: item.timestamp,
        )

        for previous in ordered_history:
            engine.transform(previous)

        behavior = engine.transform(
            event
        )

        features = np.asarray(
            [
                _event_features(
                    event,
                    behavior,
                )
            ],
            dtype=np.float32,
        )

        result = self.artifact.predict(
            features
        )

        result.update(
            {
                "timestamp": event.timestamp.isoformat(),
                "source_ip": event.src_ip,
                "destination_ip": event.dst_ip,
                "destination_port": event.dst_port,
            }
        )

        return result


def predict_from_mappings(
    artifact: ModelArtifact,
    current: Mapping,
    history: Iterable[Mapping] = (),
) -> dict:
    event = CanonicalEvent.from_mapping(
        current
    )

    history_events = [
        CanonicalEvent.from_mapping(
            item
        )
        for item in history
    ]

    return BehavioralPredictor(
        artifact
    ).predict_event(
        event,
        history_events,
    )


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: "
            "python -m backend.ml.predict_v2 "
            "<model-path>"
        )
        raise SystemExit(1)

    model_path = sys.argv[1]

    artifact = load_model_artifact(
        model_path
    )

    payload = json.load(
        sys.stdin
    )

    current = payload.get(
        "event",
        payload,
    )

    history = payload.get(
        "history",
        [],
    )

    result = predict_from_mappings(
        artifact,
        current,
        history,
    )

    print(
        json.dumps(
            result,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
