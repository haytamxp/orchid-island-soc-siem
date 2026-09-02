from __future__ import annotations

import csv
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

from backend.ml.behavior import BehaviorEngine
from backend.ml.evaluation import (
    evaluate_binary,
    select_threshold,
)
from backend.ml.feature_pipeline import (
    FEATURE_NAMES,
    build_dataset_from_csv,
)
from backend.ml.schema import CanonicalEvent
from backend.ml.temporal_split import (
    temporal_split,
)


def make_event(
    timestamp: datetime,
    *,
    src_ip: str = "10.0.0.10",
    dst_ip: str = "10.0.0.20",
    dst_port: int = 443,
    label: int = 0,
    description: str = "Normal web request",
    http_status: int = 200,
    action: str = "allowed",
    bytes_out: float = 100.0,
) -> CanonicalEvent:
    return CanonicalEvent(
        timestamp=timestamp,
        severity=(
            "low"
            if label == 0
            else "high"
        ),
        source="suricata",
        category="generic",
        description=description,
        src_ip=src_ip,
        dst_ip=dst_ip,
        dst_port=dst_port,
        username="user1",
        hostname="host1",
        url="/index",
        http_method="GET",
        http_status=http_status,
        bytes_in=200.0,
        bytes_out=bytes_out,
        action=action,
        event_id=f"event-{timestamp.timestamp()}",
        label=label,
    )


def write_dataset(
    path: Path,
    rows: list[CanonicalEvent],
) -> None:
    fields = [
        "timestamp",
        "severity",
        "source",
        "category",
        "description",
        "src_ip",
        "dst_ip",
        "dst_port",
        "username",
        "hostname",
        "url",
        "http_method",
        "http_status",
        "bytes_in",
        "bytes_out",
        "action",
        "event_id",
        "label",
    ]

    with path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fields,
        )

        writer.writeheader()

        for event in rows:
            writer.writerow(
                {
                    "timestamp": (
                        event.timestamp.isoformat()
                    ),
                    "severity": event.severity,
                    "source": event.source,
                    "category": event.category,
                    "description": event.description,
                    "src_ip": event.src_ip,
                    "dst_ip": event.dst_ip,
                    "dst_port": event.dst_port,
                    "username": event.username,
                    "hostname": event.hostname,
                    "url": event.url,
                    "http_method": event.http_method,
                    "http_status": event.http_status,
                    "bytes_in": event.bytes_in,
                    "bytes_out": event.bytes_out,
                    "action": event.action,
                    "event_id": event.event_id,
                    "label": event.label,
                }
            )


def test_behavior_uses_history_only() -> None:
    engine = BehaviorEngine()

    first = make_event(
        datetime(
            2026,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        label=1,
        action="failed",
    )

    first_features = (
        engine.transform(first)
    )

    assert (
        first_features[
            "behavior_events_5m"
        ]
        == 0.0
    )

    assert (
        first_features[
            "failed_auth_5m"
        ]
        == 0.0
    )

    second = make_event(
        datetime(
            2026,
            1,
            1,
            0,
            1,
            tzinfo=timezone.utc,
        ),
    )

    second_features = (
        engine.transform(second)
    )

    assert (
        second_features[
            "behavior_events_5m"
        ]
        == 1.0
    )

    assert (
        second_features[
            "failed_auth_5m"
        ]
        == 1.0
    )


def test_feature_pipeline_is_leakage_resistant(
    tmp_path: Path,
) -> None:
    base_time = datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc,
    )

    rows = [
        make_event(
            base_time
            + timedelta(
                minutes=index
            ),
            label=index % 2,
            description=(
                "Generic event A"
                if index % 2 == 0
                else "Generic event B"
            ),
        )
        for index in range(20)
    ]

    path = (
        tmp_path
        / "events.csv"
    )

    write_dataset(
        path,
        rows,
    )

    dataset = (
        build_dataset_from_csv(path)
    )

    assert dataset.features.shape == (
        20,
        len(FEATURE_NAMES),
    )

    assert (
        "label"
        not in dataset.feature_names
    )

    assert (
        "category"
        not in dataset.feature_names
    )

    assert set(
        np.unique(
            dataset.labels
        )
    ) == {0, 1}


def test_temporal_split_preserves_order() -> None:
    timestamps = list(
        range(100)
    )

    split = temporal_split(
        timestamps,
        train_ratio=0.70,
        validation_ratio=0.15,
    )

    assert (
        split.train_indices[-1]
        < split.validation_indices[0]
    )

    assert (
        split.validation_indices[-1]
        < split.test_indices[0]
    )

    assert len(
        set(split.train_indices)
        & set(split.validation_indices)
    ) == 0

    assert len(
        set(split.validation_indices)
        & set(split.test_indices)
    ) == 0


def test_threshold_uses_validation_only() -> None:
    y_validation = np.array(
        [0, 0, 0, 1, 1, 1],
        dtype=np.int8,
    )

    validation_scores = np.array(
        [0.05, 0.10, 0.20, 0.70, 0.85, 0.95],
        dtype=np.float64,
    )

    threshold = select_threshold(
        y_validation,
        validation_scores,
        minimum_precision=0.70,
    )

    assert 0.0 <= threshold <= 1.0

    y_test = np.array(
        [0, 0, 1, 1],
        dtype=np.int8,
    )

    test_scores = np.array(
        [0.10, 0.40, 0.80, 0.90],
        dtype=np.float64,
    )

    result = evaluate_binary(
        y_test,
        test_scores,
        threshold,
    )

    assert 0.0 <= result.precision <= 1.0
    assert 0.0 <= result.recall <= 1.0
    assert 0.0 <= result.f1 <= 1.0
    assert 0.0 <= result.pr_auc <= 1.0
