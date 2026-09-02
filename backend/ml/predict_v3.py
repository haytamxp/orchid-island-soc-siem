"""
Inference for the behavior-first V3 model.
"""

from __future__ import annotations

import json
import sys

import numpy as np

from backend.ml.behavior import BehaviorEngine
from backend.ml.behavior_features_v3 import (
    build_behavior_features,
)
from backend.ml.model_io import (
    load_model_artifact,
)
from backend.ml.schema import CanonicalEvent


def predict(
    model_path: str,
    current: dict,
    history: list[dict] | None = None,
) -> dict:

    artifact = load_model_artifact(
        model_path
    )

    event = CanonicalEvent.from_mapping(
        current
    )

    previous_events = [
        CanonicalEvent.from_mapping(
            item
        )
        for item in (
            history or []
        )
    ]

    previous_events = sorted(
        previous_events,
        key=lambda item: item.timestamp,
    )

    engine = BehaviorEngine()

    for previous in previous_events:
        if previous.timestamp <= event.timestamp:
            engine.transform(
                previous
            )

    behavior = engine.transform(
        event
    )

    features = np.asarray(
        [
            build_behavior_features(
                event,
                behavior,
            )
        ],
        dtype=np.float32,
    )

    result = artifact.predict(
        features
    )

    result.update(
        {
            "timestamp": (
                event.timestamp.isoformat()
            ),
            "source_ip": event.src_ip,
            "destination_ip": event.dst_ip,
            "destination_port": (
                event.dst_port
            ),
            "model": "behavior-first-v3",
        }
    )

    return result


def main() -> None:
    if len(sys.argv) != 2:
        print(
            "Usage: "
            "python -m backend.ml.predict_v3 "
            "<model-path>"
        )
        raise SystemExit(1)

    payload = json.load(
        sys.stdin
    )

    result = predict(
        sys.argv[1],
        payload.get(
            "event",
            payload,
        ),
        payload.get(
            "history",
            [],
        ),
    )

    print(
        json.dumps(
            result,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
