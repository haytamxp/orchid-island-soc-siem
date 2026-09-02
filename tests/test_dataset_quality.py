from __future__ import annotations

import csv
from datetime import datetime, timedelta, timezone
from pathlib import Path

from backend.ml.dataset_audit import (
    audit_dataset,
)
from backend.ml.feature_pipeline import (
    load_events_csv,
)


def write_rows(
    path: Path,
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

    start = datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc,
    )

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

        for index in range(10):
            writer.writerow(
                {
                    "timestamp": (
                        start
                        + timedelta(
                            minutes=index
                        )
                    ).isoformat(),
                    "severity": (
                        "low"
                        if index % 2 == 0
                        else "high"
                    ),
                    "source": "suricata",
                    "category": "generic",
                    "description": "Generic event",
                    "src_ip": "10.0.0.10",
                    "dst_ip": "10.0.0.20",
                    "dst_port": (
                        443
                        if index % 2 == 0
                        else 445
                    ),
                    "username": "alice",
                    "hostname": "web01",
                    "url": "/",
                    "http_method": "GET",
                    "http_status": 200,
                    "bytes_in": 100,
                    "bytes_out": 200,
                    "action": "allowed",
                    "event_id": f"e-{index}",
                    "label": index % 2,
                }
            )


def test_dataset_audit_reports_correct_counts(
    tmp_path: Path,
) -> None:
    path = (
        tmp_path
        / "dataset.csv"
    )

    write_rows(path)

    report = audit_dataset(
        path
    )

    assert report["rows"] == 10
    assert report["benign"] == 5
    assert report["malicious"] == 5
    assert (
        report["duplicate_event_ids"]
        == 0
    )
    assert (
        report["out_of_order_timestamps"]
        == 0
    )


def test_dataset_is_chronological(
    tmp_path: Path,
) -> None:
    path = (
        tmp_path
        / "dataset.csv"
    )

    write_rows(path)

    events = load_events_csv(
        path
    )

    timestamps = [
        event.timestamp
        for event in events
    ]

    assert timestamps == sorted(
        timestamps
    )
