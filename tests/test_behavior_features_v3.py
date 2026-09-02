from __future__ import annotations

from datetime import datetime, timedelta, timezone

from backend.ml.behavior import BehaviorEngine
from backend.ml.behavior_features_v3 import (
    FEATURE_NAMES,
    build_behavior_features,
)
from backend.ml.schema import CanonicalEvent


def event(
    timestamp: datetime,
    *,
    port: int = 443,
    status: int = 200,
    action: str = "allowed",
    bytes_out: float = 100.0,
) -> CanonicalEvent:
    return CanonicalEvent(
        timestamp=timestamp,
        severity="critical",
        source="unknown",
        category="SQL_INJECTION",
        description=(
            "SQL injection attack detected "
            "MALWARE BRUTE_FORCE"
        ),
        src_ip="8.8.8.8",
        dst_ip="10.0.0.10",
        dst_port=port,
        username="alice",
        hostname="web01",
        url="/properties?id=1' UNION SELECT",
        http_method="GET",
        http_status=status,
        bytes_in=200.0,
        bytes_out=bytes_out,
        action=action,
        label=1,
    )


def test_v3_feature_count() -> None:
    now = datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc,
    )

    engine = BehaviorEngine()

    current = event(now)

    behavior = engine.transform(
        current
    )

    features = build_behavior_features(
        current,
        behavior,
    )

    assert len(features) == len(
        FEATURE_NAMES
    )


def test_current_event_not_in_history() -> None:
    now = datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc,
    )

    engine = BehaviorEngine()

    current = event(now)

    behavior = engine.transform(
        current
    )

    assert (
        behavior[
            "behavior_events_5m"
        ]
        == 0.0
    )


def test_future_event_is_not_used() -> None:
    now = datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc,
    )

    engine = BehaviorEngine()

    current = event(now)

    future = event(
        now
        + timedelta(
            minutes=5
        )
    )

    engine.transform(
        future
    )

    behavior = engine.transform(
        current
    )

    assert (
        behavior[
            "behavior_events_5m"
        ]
        == 0.0
    )

    assert (
        behavior[
            "failed_auth_5m"
        ]
        == 0.0
    )


def test_future_event_does_not_change_previous_time() -> None:
    now = datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc,
    )

    engine = BehaviorEngine()

    future = event(
        now
        + timedelta(
            minutes=5
        )
    )

    current = event(now)

    engine.transform(
        future
    )

    behavior = engine.transform(
        current
    )

    assert (
        behavior[
            "seconds_since_previous"
        ]
        == 3600.0
    )


def test_older_event_after_future_is_still_safe() -> None:
    now = datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc,
    )

    engine = BehaviorEngine()

    future = event(
        now
        + timedelta(
            minutes=10
        )
    )

    middle = event(
        now
        + timedelta(
            minutes=5
        )
    )

    engine.transform(
        future
    )

    engine.transform(
        middle
    )

    behavior = engine.transform(
        event(now)
    )

    assert (
        behavior[
            "behavior_events_5m"
        ]
        == 0.0
    )

    assert (
        behavior[
            "seconds_since_previous"
        ]
        == 3600.0
    )


def test_v3_does_not_expose_metadata_features() -> None:
    forbidden = {
        "severity_score",
        "source",
        "category",
        "description_length_log",
        "description_special_chars",
        "description_has_spaces",
    }

    assert not (
        forbidden
        & set(FEATURE_NAMES)
    )
