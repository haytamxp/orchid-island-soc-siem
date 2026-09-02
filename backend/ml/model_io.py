"""
Safe model-artifact loading and scoring support.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np


class ModelArtifact:
    def __init__(
        self,
        model: Any,
        feature_names: list[str],
        threshold: float,
        version: str,
    ) -> None:
        self.model = model
        self.feature_names = feature_names
        self.threshold = float(threshold)
        self.version = version

    def predict_proba(
        self,
        features: np.ndarray,
    ) -> np.ndarray:
        matrix = np.asarray(
            features,
            dtype=np.float32,
        )

        if matrix.ndim == 1:
            matrix = matrix.reshape(
                1,
                -1,
            )

        if matrix.shape[1] != len(
            self.feature_names
        ):
            raise ValueError(
                "Feature width does not match "
                "the trained model: "
                f"{matrix.shape[1]} != "
                f"{len(self.feature_names)}"
            )

        return self.model.predict_proba(
            matrix
        )[:, 1]

    def predict(
        self,
        features: np.ndarray,
    ) -> dict[str, Any]:
        probability = float(
            self.predict_proba(
                features
            )[0]
        )

        return {
            "probability": probability,
            "malicious": (
                probability
                >= self.threshold
            ),
            "threshold": self.threshold,
            "version": self.version,
        }


def load_model_artifact(
    path: str | Path,
) -> ModelArtifact:
    model_path = Path(path)

    if not model_path.exists():
        raise FileNotFoundError(
            f"Model artifact not found: "
            f"{model_path}"
        )

    payload = joblib.load(
        model_path
    )

    if not isinstance(
        payload,
        dict,
    ):
        raise ValueError(
            "Invalid model artifact format"
        )

    required = {
        "model",
        "feature_names",
        "threshold",
        "version",
    }

    missing = required - set(
        payload.keys()
    )

    if missing:
        raise ValueError(
            "Model artifact missing fields: "
            f"{sorted(missing)}"
        )

    feature_names = payload[
        "feature_names"
    ]

    if not isinstance(
        feature_names,
        list,
    ):
        raise ValueError(
            "feature_names must be a list"
        )

    return ModelArtifact(
        model=payload["model"],
        feature_names=feature_names,
        threshold=float(
            payload["threshold"]
        ),
        version=str(
            payload["version"]
        ),
    )
