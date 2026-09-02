"""
Training-dataset quality checks.
"""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path
from typing import Any

from backend.ml.feature_pipeline import load_events_csv


def audit_dataset(path: str | Path) -> dict[str, Any]:
    events = load_events_csv(path)

    labels = [
        event.label
        for event in events
    ]

    sources = Counter(
        event.source
        for event in events
    )

    severities = Counter(
        event.severity
        for event in events
    )

    timestamps = [
        event.timestamp
        for event in events
    ]

    duplicate_event_ids = 0

    event_ids = [
        event.event_id
        for event in events
        if event.event_id
    ]

    duplicate_event_ids = (
        len(event_ids)
        - len(set(event_ids))
    )

    out_of_order = sum(
        1
        for previous, current in zip(
            timestamps,
            timestamps[1:],
        )
        if current < previous
    )

    benign = sum(
        label == 0
        for label in labels
    )

    malicious = sum(
        label == 1
        for label in labels
    )

    total = len(events)

    return {
        "rows": total,
        "benign": benign,
        "malicious": malicious,
        "malicious_ratio": (
            malicious / total
            if total
            else 0.0
        ),
        "sources": dict(sources),
        "severities": dict(severities),
        "duplicate_event_ids": duplicate_event_ids,
        "out_of_order_timestamps": out_of_order,
        "first_timestamp": (
            timestamps[0].isoformat()
            if timestamps
            else None
        ),
        "last_timestamp": (
            timestamps[-1].isoformat()
            if timestamps
            else None
        ),
    }


def print_audit(path: str | Path) -> None:
    report = audit_dataset(path)

    print(
        f"Rows: {report['rows']}"
    )

    print(
        f"Benign: {report['benign']}"
    )

    print(
        f"Malicious: {report['malicious']}"
    )

    print(
        "Malicious ratio: "
        f"{report['malicious_ratio']:.2%}"
    )

    print(
        "Duplicate event IDs: "
        f"{report['duplicate_event_ids']}"
    )

    print(
        "Out-of-order timestamps: "
        f"{report['out_of_order_timestamps']}"
    )

    print(
        "Sources: "
        f"{report['sources']}"
    )

    print(
        "Severities: "
        f"{report['severities']}"
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Audit security ML dataset"
    )

    parser.add_argument(
        "dataset"
    )

    args = parser.parse_args()

    print_audit(
        args.dataset
    )
