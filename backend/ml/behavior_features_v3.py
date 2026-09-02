"""
Behavior-first feature definitions for Orchid Island ML V3.
"""

from __future__ import annotations

import math

from backend.ml.schema import CanonicalEvent


FEATURE_NAMES = [
    "dst_port_log",
    "is_security_protocol_port",
    "is_common_web_port",
    "has_src_ip",
    "has_dst_ip",
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
    "url_has_query",
    "url_query_params",
    "url_path_depth",
    "url_special_chars",
    "is_weekend",
    "is_off_hours",
    "hour_sin",
    "hour_cos",
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


def _safe_log(
    value: float,
) -> float:
    return math.log1p(
        max(
            0.0,
            value,
        )
    )


def _special_count(
    value: str,
) -> float:
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


def url_features(
    url: str,
) -> tuple[float, float, float, float]:
    if not url:
        return (
            0.0,
            0.0,
            0.0,
            0.0,
        )

    path = url.split(
        "?",
        1,
    )[0]

    return (
        float("?" in url),
        float(
            url.count("&")
            + (
                1
                if "?" in url
                and url.split("?", 1)[1]
                else 0
            )
        ),
        float(
            len(
                [
                    part
                    for part in path.split("/")
                    if part
                ]
            )
        ),
        _special_count(url),
    )


def build_behavior_features(
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

    (
        url_has_query,
        url_query_params,
        url_path_depth,
        url_special_chars,
    ) = url_features(
        event.url
    )

    status = float(
        event.http_status
    )

    features = [
        _safe_log(
            event.dst_port
        ),
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
        float(bool(event.src_ip)),
        float(bool(event.dst_ip)),
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
        _safe_log(
            event.bytes_in
        ),
        _safe_log(
            event.bytes_out
        ),
        url_has_query,
        url_query_params,
        url_path_depth,
        url_special_chars,
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
    ]

    features.extend(
        behavior[name]
        for name in FEATURE_NAMES[23:]
    )

    if len(features) != len(
        FEATURE_NAMES
    ):
        raise ValueError(
            "V3 feature count mismatch"
        )

    return features
