from __future__ import annotations

import json
from pathlib import Path

import pytest

from backend.ml.trainer_v3 import (
    positive_weight,
)
from backend.ml.feature_pipeline_v3 import (
    build_dataset_from_csv,
)

import numpy as np


def test_positive_weight() -> None:
    labels = np.asarray(
        [
            0,
            0,
            0,
            1,
        ],
        dtype=np.int8,
    )

    assert positive_weight(
        labels
    ) == pytest.approx(3.0)


def test_positive_weight_rejects_missing_class() -> None:
    labels = np.zeros(
        10,
        dtype=np.int8,
    )

    with pytest.raises(
        ValueError
    ):
        positive_weight(
            labels
        )


def test_v3_dataset_is_binary(
    tmp_path: Path,
) -> None:
    path = (
        tmp_path
        / "dataset.csv"
    )

    path.write_text(
        (
            "timestamp,severity,source,category,"
            "description,src_ip,dst_ip,dst_port,"
            "username,hostname,url,http_method,"
            "http_status,bytes_in,bytes_out,"
            "action,event_id,label\n"
            "2026-01-01T00:00:00,"
            "high,suricata,generic,test,"
            "1.1.1.1,10.0.0.10,443,alice,"
            "web01,/,GET,200,100,100,allowed,e1,0\n"
            "2026-01-01T00:01:00,"
            "low,wazuh,generic,test,"
            "1.1.1.2,10.0.0.20,445,bob,"
            "app01,/,GET,200,100,100,denied,e2,1\n"
        ),
        encoding="utf-8",
    )

    dataset = build_dataset_from_csv(
        path
    )

    assert dataset.features.shape[1] == 43
    assert set(
        dataset.labels.tolist()
    ) == {0, 1}


def test_v3_feature_names_are_unique() -> None:
    from backend.ml.behavior_features_v3 import (
        FEATURE_NAMES,
    )

    assert len(
        FEATURE_NAMES
    ) == len(
        set(FEATURE_NAMES)
    )
