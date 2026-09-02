from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pytest

from backend.ml.model_io import (
    ModelArtifact,
    load_model_artifact,
)


class DummyModel:
    def predict_proba(
        self,
        matrix: np.ndarray,
    ) -> np.ndarray:
        rows = len(matrix)

        return np.column_stack(
            [
                np.full(
                    rows,
                    0.25,
                ),
                np.full(
                    rows,
                    0.75,
                ),
            ]
        )


def test_model_artifact_prediction() -> None:
    artifact = ModelArtifact(
        model=DummyModel(),
        feature_names=[
            "feature_a",
            "feature_b",
        ],
        threshold=0.60,
        version="test",
    )

    result = artifact.predict(
        np.array(
            [[1.0, 2.0]],
            dtype=np.float32,
        )
    )

    assert result[
        "probability"
    ] == pytest.approx(0.75)

    assert result[
        "malicious"
    ] is True

    assert result[
        "threshold"
    ] == pytest.approx(0.60)


def test_model_artifact_rejects_wrong_feature_width() -> None:
    artifact = ModelArtifact(
        model=DummyModel(),
        feature_names=[
            "feature_a",
            "feature_b",
        ],
        threshold=0.5,
        version="test",
    )

    with pytest.raises(
        ValueError
    ):
        artifact.predict(
            np.array(
                [[1.0, 2.0, 3.0]],
                dtype=np.float32,
            )
        )


def test_load_model_artifact(
    tmp_path: Path,
) -> None:
    path = (
        tmp_path
        / "model.joblib"
    )

    joblib.dump(
        {
            "model": DummyModel(),
            "feature_names": [
                "feature_a",
                "feature_b",
            ],
            "threshold": 0.55,
            "version": "v2",
        },
        path,
    )

    artifact = load_model_artifact(
        path
    )

    assert artifact.version == "v2"
    assert artifact.feature_names == [
        "feature_a",
        "feature_b",
    ]
    assert artifact.threshold == pytest.approx(
        0.55
    )


def test_missing_model_artifact(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        FileNotFoundError
    ):
        load_model_artifact(
            tmp_path
            / "missing.joblib"
        )
