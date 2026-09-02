from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pytest

from backend.ml.model_io import (
    ModelArtifact,
)
from backend.ml.robustness import (
    compare_results,
    load_features_for_model,
    BenchmarkResult,
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


def minimal_dataset(
    path: Path,
) -> None:
    path.write_text(
        (
            "timestamp,severity,source,category,"
            "description,src_ip,dst_ip,dst_port,"
            "username,hostname,url,http_method,"
            "http_status,bytes_in,bytes_out,"
            "action,event_id,label\n"
            "2026-01-01T00:00:00,"
            "low,suricata,generic,event,"
            "1.1.1.1,10.0.0.10,443,alice,"
            "web01,/,GET,200,100,100,allowed,e1,0\n"
            "2026-01-01T00:01:00,"
            "high,wazuh,generic,event,"
            "1.1.1.1,10.0.0.10,445,alice,"
            "web01,/,GET,403,100,100,denied,e2,1\n"
        ),
        encoding="utf-8",
    )


def test_v3_artifact_uses_v3_pipeline(
    tmp_path: Path,
) -> None:
    path = (
        tmp_path
        / "dataset.csv"
    )

    minimal_dataset(path)

    artifact = ModelArtifact(
        model=DummyModel(),
        feature_names=[
            f"feature_{i}"
            for i in range(43)
        ],
        threshold=0.5,
        version="v3",
    )

    dataset = load_features_for_model(
        artifact,
        str(path),
    )

    assert dataset.features.shape[1] == 43


def test_v2_artifact_uses_legacy_pipeline(
    tmp_path: Path,
) -> None:
    path = (
        tmp_path
        / "dataset.csv"
    )

    minimal_dataset(path)

    artifact = ModelArtifact(
        model=DummyModel(),
        feature_names=[
            f"feature_{i}"
            for i in range(48)
        ],
        threshold=0.5,
        version="v2",
    )

    dataset = load_features_for_model(
        artifact,
        str(path),
    )

    assert dataset.features.shape[1] == 48


def test_unknown_feature_schema_is_rejected(
    tmp_path: Path,
) -> None:
    path = (
        tmp_path
        / "dataset.csv"
    )

    minimal_dataset(path)

    artifact = ModelArtifact(
        model=DummyModel(),
        feature_names=[
            "one",
            "two",
        ],
        threshold=0.5,
        version="unknown",
    )

    with pytest.raises(
        ValueError,
    ):
        load_features_for_model(
            artifact,
            str(path),
        )


def test_compare_results_uses_first_result_as_baseline() -> None:
    baseline = BenchmarkResult(
        name="baseline",
        samples=100,
        malicious_rate=0.2,
        precision=0.95,
        recall=0.90,
        f1=0.925,
        pr_auc=0.96,
        roc_auc=0.97,
        false_positive_rate=0.01,
        false_negative_rate=0.10,
        threshold=0.45,
    )

    shifted = BenchmarkResult(
        name="shifted",
        samples=100,
        malicious_rate=0.2,
        precision=0.90,
        recall=0.80,
        f1=0.847,
        pr_auc=0.89,
        roc_auc=0.92,
        false_positive_rate=0.02,
        false_negative_rate=0.20,
        threshold=0.45,
    )

    report = compare_results(
        [
            baseline,
            shifted,
        ]
    )

    assert (
        report["baseline"]["name"]
        == "baseline"
    )

    assert (
        report["results"][1]["delta_f1"]
        == pytest.approx(
            shifted.f1
            - baseline.f1
        )
    )
