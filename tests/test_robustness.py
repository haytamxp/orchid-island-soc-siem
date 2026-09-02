from __future__ import annotations

import csv
from pathlib import Path

from backend.ml.stress_dataset import (
    anonymize_semantics,
    combined_shift,
    read_rows,
    shift_severity,
    shift_sources,
)


def sample_rows() -> list[dict[str, str]]:
    return [
        {
            "timestamp": "2026-01-01T00:00:00",
            "severity": "critical",
            "source": "suricata",
            "category": "network",
            "description": "Network security event",
            "src_ip": "1.1.1.1",
            "dst_ip": "10.0.0.10",
            "dst_port": "443",
            "username": "admin",
            "hostname": "web01",
            "url": "/",
            "http_method": "GET",
            "http_status": "403",
            "bytes_in": "100",
            "bytes_out": "200",
            "action": "blocked",
            "event_id": "1",
            "label": "1",
        }
    ]


def test_anonymize_keeps_labels() -> None:
    rows = sample_rows()

    transformed = anonymize_semantics(
        rows
    )

    assert transformed[0]["label"] == "1"
    assert transformed[0][
        "category"
    ] == "generic"


def test_severity_shift_only_changes_severity() -> None:
    rows = sample_rows()

    transformed = shift_severity(
        rows
    )

    assert transformed[0][
        "severity"
    ] == "high"

    assert transformed[0][
        "label"
    ] == "1"


def test_source_shift_preserves_labels() -> None:
    rows = sample_rows()

    transformed = shift_sources(
        rows
    )

    assert transformed[0][
        "source"
    ] == "wazuh"

    assert transformed[0][
        "label"
    ] == "1"


def test_combined_shift_preserves_attack_identity() -> None:
    rows = sample_rows()

    transformed = combined_shift(
        rows
    )

    assert transformed[0][
        "label"
    ] == "1"

    assert transformed[0][
        "category"
    ] == "generic"
