"""
Leakage-resistant feature pipeline.

The label and semantic attack category are never model features.
"""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import numpy as np

from backend.ml.behavior import BehaviorEngine
from backend.ml.schema import CanonicalEvent


SEVERITY_MAP = {
    "low": 1.0,
    "medium": 2.0,
    "high": 3.0,
    "critical": 4.0,
}

METHOD_MAP = {
    "": 0.0,
    "GET": 1.0,
    "POST": 2.0,
    "PUT": 3.0,
    "PATCH": 4.0,
    "DELETE": 5.0,
    "HEAD": 6.0,
    "OPTIONS": 7.0,
}


@dataclass(slots=True)
class Dataset:
    events: list[CanonicalEvent]
    timestamps: list[object]
    features: np.ndarray
    labels: np.ndarray
    feature_names: list[str]


def _safe_log(value: float) -> float:
    return math.log1p(
        max(0.0, value)
    )


def _special_count(value: str) -> float:
    if not value:
        return 0.0

    chars = (
        "'",
        '"',
        "<",
        ">",
        ";",
        "|",
        "`",
        "$",
        "{",
        "}",
        "(",
        ")",
    )

    return float(
        sum(
            value.count(char)
            for char in chars
        )
    )


def _url_structure(url: str) -> dict[str, float]:
    if not url:
        return {
            "url_has_query": 0.0,
            "url_query_params": 0.0,
            "url_path_depth": 0.0,
            "url_special_chars": 0.0,
        }

    return {
        "url_has_query": float(
            "?" in url
        ),
        "url_query_params": float(
            url.count("&")
            + (
                1
                if "?" in url
                and url.split("?", 1)[1]
                else 0
            )
        ),
        "url_path_depth": float(
            len(
                [
                    x
                    for x in url.split("?", 1)[0].split("/")
                    if x
                ]
            )
        ),
        "url_special_chars": _special_count(url),
    }


BASE_FEATURE_NAMES = [
    "severity_score",
    "known_security_source",
    "has_src_ip",
    "has_dst_ip",
    "dst_port_log",
    "is_security_protocol_port",
    "is_common_web_or_service_port",
    "has_username",
    "has_hostname",
    "has_url",
    "http_method_code",
    "http_2xx",
    "http_3xx",
    "http_4xx",
    "http_5xx",
    "bytes_in_log",
    "bytes_out_log",
    "description_length_log",
    "description_special_chars",
    "description_has_spaces",
    "is_weekend",
    "is_off_hours",
    "hour_sin",
    "hour_cos",
    "url_has_query",
    "url_query_params",
    "url_path_depth",
    "url_special_chars",
]

BEHAVIOR_FEATURE_NAMES = [
    "behavior_events_1m",
    "behavior_events_5m",
    "behavior_events_1h",
    "failed_auth_1m",
    "failed_auth_5m",
    "failed_auth_1h",
    "unique_dst_ips_5m",
    "unique_dst_ports_5m",
    "unique_dst_ports_1h",
    "unique_users_5m",
    "http_4xx_rate_5m",
    "http_5xx_rate_5m",
    "bytes_out_5m",
    "bytes_out_1h",
    "request_burst_ratio",
    "unique_port_rate",
    "seconds_since_previous",
    "historical_destination_seen",
    "historical_port_seen",
    "current_failed_auth",
]

FEATURE_NAMES = (
    BASE_FEATURE_NAMES
    + BEHAVIOR_FEATURE_NAMES
)


def _event_features(
    event: CanonicalEvent,
    behavior: dict[str, float],
) -> list[float]:
    hour = (
        event.timestamp.hour
        + event.timestamp.minute / 60.0
    )

    angle = (
        2.0
        * math.pi
        * hour
        / 24.0
    )

    url_features = _url_structure(
        event.url
    )

    status = float(
        event.http_status
    )

    result = [
        SEVERITY_MAP.get(
            event.severity,
            0.0,
        ),
        float(
            event.source
            in {
                "wazuh",
                "suricata",
                "cloudflare",
            }
        ),
        float(bool(event.src_ip)),
        float(bool(event.dst_ip)),
        _safe_log(event.dst_port),
        float(
            event.dst_port
            in {
                53,
                88,
                389,
                443,
                445,
                636,
                3389,
                5985,
                5986,
            }
        ),
        float(
            event.dst_port
            in {
                22,
                23,
                80,
                443,
                8080,
                8443,
            }
        ),
        float(bool(event.username)),
        float(bool(event.hostname)),
        float(bool(event.url)),
        METHOD_MAP.get(
            event.http_method,
            0.0,
        ),
        float(
            200 <= status <= 299
        ),
        float(
            300 <= status <= 399
        ),
        float(
            400 <= status <= 499
        ),
        float(
            500 <= status <= 599
        ),
        _safe_log(event.bytes_in),
        _safe_log(event.bytes_out),
        _safe_log(
            len(event.description)
        ),
        _special_count(
            event.description
        ),
        float(
            " " in event.description
        ),
        float(
            event.timestamp.weekday()
            >= 5
        ),
        float(
            event.timestamp.hour < 6
            or event.timestamp.hour >= 22
        ),
        math.sin(angle),
        math.cos(angle),
        url_features[
            "url_has_query"
        ],
        url_features[
            "url_query_params"
        ],
        url_features[
            "url_path_depth"
        ],
        url_features[
            "url_special_chars"
        ],
    ]

    result.extend(
        behavior[name]
        for name in BEHAVIOR_FEATURE_NAMES
    )

    return result


def load_events_csv(
    path: str | Path,
) -> list[CanonicalEvent]:
    csv_path = Path(path)

    if not csv_path.exists():
        raise FileNotFoundError(
            f"Training dataset not found: {csv_path}"
        )

    events: list[CanonicalEvent] = []

    with csv_path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        reader = csv.DictReader(
            handle
        )

        if reader.fieldnames is None:
            raise ValueError(
                "CSV file does not contain a header"
            )

        for row_number, row in enumerate(
            reader,
            start=2,
        ):
            try:
                event = (
                    CanonicalEvent.from_mapping(
                        row
                    )
                )
            except ValueError as exc:
                raise ValueError(
                    f"Invalid event at CSV row "
                    f"{row_number}: {exc}"
                ) from exc

            if event.label is None:
                raise ValueError(
                    f"Missing label at CSV row "
                    f"{row_number}"
                )

            events.append(event)

    if not events:
        raise ValueError(
            "Training dataset is empty"
        )

    return sorted(
        events,
        key=lambda event: event.timestamp,
    )


def build_dataset(
    events: Sequence[CanonicalEvent],
) -> Dataset:
    ordered = sorted(
        events,
        key=lambda event: event.timestamp,
    )

    behavior_engine = BehaviorEngine()

    feature_rows: list[list[float]] = []
    labels: list[int] = []

    for event in ordered:
        behavior = (
            behavior_engine.transform(
                event
            )
        )

        feature_rows.append(
            _event_features(
                event,
                behavior,
            )
        )

        if event.label is None:
            raise ValueError(
                "All training events must contain labels"
            )

        labels.append(
            event.label
        )

    features = np.asarray(
        feature_rows,
        dtype=np.float32,
    )

    label_array = np.asarray(
        labels,
        dtype=np.int8,
    )

    if features.ndim != 2:
        raise ValueError(
            f"Expected 2D matrix, got {features.shape}"
        )

    if features.shape[1] != len(
        FEATURE_NAMES
    ):
        raise ValueError(
            "Feature name count does not match matrix width"
        )

    if set(
        np.unique(label_array)
    ) - {0, 1}:
        raise ValueError(
            "Labels must be binary"
        )

    return Dataset(
        events=ordered,
        timestamps=[
            event.timestamp
            for event in ordered
        ],
        features=features,
        labels=label_array,
        feature_names=list(
            FEATURE_NAMES
        ),
    )


def build_dataset_from_csv(
    path: str | Path,
) -> Dataset:
    return build_dataset(
        load_events_csv(path)
    )
