"""
Historical behavioral feature extraction.

The engine is time-aware and never allows future events to influence the
behavioral state of an earlier event.
"""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import timedelta
from typing import Deque

from backend.ml.schema import CanonicalEvent


@dataclass(slots=True)
class HistoricalEvent:
    timestamp: object
    src_ip: str
    dst_ip: str
    dst_port: int
    username: str
    http_status: int
    bytes_out: float
    failed_auth: bool


class BehaviorEngine:
    WINDOW_1M = timedelta(minutes=1)
    WINDOW_5M = timedelta(minutes=5)
    WINDOW_1H = timedelta(hours=1)

    def __init__(self) -> None:
        self.by_source: dict[
            str,
            Deque[HistoricalEvent],
        ] = defaultdict(deque)

        self.last_seen: dict[str, object] = {}

    @staticmethod
    def _source_key(
        event: CanonicalEvent,
    ) -> str:
        return event.src_ip or "__unknown_source__"

    @staticmethod
    def _failed_auth(
        event: CanonicalEvent,
    ) -> bool:
        text = (
            f"{event.action} "
            f"{event.description}"
        ).lower()

        markers = (
            "failed",
            "failure",
            "denied",
            "invalid",
            "unauthorized",
            "authentication error",
        )

        return any(
            marker in text
            for marker in markers
        )

    @staticmethod
    def _prune(
        queue: Deque[HistoricalEvent],
        cutoff: object,
    ) -> None:
        """
        Remove stale events without assuming the queue is perfectly ordered.
        """

        remaining = [
            item
            for item in queue
            if item.timestamp >= cutoff
        ]

        remaining.sort(
            key=lambda item: item.timestamp
        )

        queue.clear()
        queue.extend(remaining)

    @staticmethod
    def _window(
        queue: Deque[HistoricalEvent],
        now: object,
        window: timedelta,
    ) -> list[HistoricalEvent]:
        cutoff = now - window

        return [
            item
            for item in queue
            if cutoff <= item.timestamp <= now
        ]

    @staticmethod
    def _stats(
        items: list[HistoricalEvent],
    ) -> dict[str, float]:
        if not items:
            return {
                "count": 0.0,
                "unique_dst_ips": 0.0,
                "unique_dst_ports": 0.0,
                "unique_users": 0.0,
                "failed_auth": 0.0,
                "http_4xx": 0.0,
                "http_5xx": 0.0,
                "http_total": 0.0,
                "bytes_out": 0.0,
            }

        http_items = [
            item
            for item in items
            if item.http_status > 0
        ]

        return {
            "count": float(len(items)),
            "unique_dst_ips": float(
                len(
                    {
                        item.dst_ip
                        for item in items
                        if item.dst_ip
                    }
                )
            ),
            "unique_dst_ports": float(
                len(
                    {
                        item.dst_port
                        for item in items
                        if item.dst_port > 0
                    }
                )
            ),
            "unique_users": float(
                len(
                    {
                        item.username
                        for item in items
                        if item.username
                    }
                )
            ),
            "failed_auth": float(
                sum(
                    1
                    for item in items
                    if item.failed_auth
                )
            ),
            "http_4xx": float(
                sum(
                    1
                    for item in http_items
                    if 400 <= item.http_status <= 499
                )
            ),
            "http_5xx": float(
                sum(
                    1
                    for item in http_items
                    if 500 <= item.http_status <= 599
                )
            ),
            "http_total": float(
                len(http_items)
            ),
            "bytes_out": float(
                sum(
                    item.bytes_out
                    for item in items
                )
            ),
        }

    def transform(
        self,
        event: CanonicalEvent,
    ) -> dict[str, float]:
        key = self._source_key(event)
        queue = self.by_source[key]

        self._prune(
            queue,
            event.timestamp - self.WINDOW_1H,
        )

        history_1m = self._window(
            queue,
            event.timestamp,
            self.WINDOW_1M,
        )

        history_5m = self._window(
            queue,
            event.timestamp,
            self.WINDOW_5M,
        )

        history_1h = self._window(
            queue,
            event.timestamp,
            self.WINDOW_1H,
        )

        stats_1m = self._stats(
            history_1m
        )

        stats_5m = self._stats(
            history_5m
        )

        stats_1h = self._stats(
            history_1h
        )

        prior_timestamps = [
            item.timestamp
            for item in queue
            if item.timestamp <= event.timestamp
        ]

        previous_time = (
            max(prior_timestamps)
            if prior_timestamps
            else None
        )

        if previous_time is None:
            seconds_since_previous = 3600.0
        else:
            seconds_since_previous = max(
                0.0,
                (
                    event.timestamp
                    - previous_time
                ).total_seconds(),
            )

        request_burst = (
            stats_1m["count"]
            / max(
                stats_5m["count"] / 5.0,
                1.0,
            )
        )

        unique_port_rate = (
            stats_5m["unique_dst_ports"]
            / max(
                stats_5m["count"],
                1.0,
            )
        )

        http_4xx_rate = (
            stats_5m["http_4xx"]
            / max(
                stats_5m["http_total"],
                1.0,
            )
        )

        http_5xx_rate = (
            stats_5m["http_5xx"]
            / max(
                stats_5m["http_total"],
                1.0,
            )
        )

        historical_destination_seen = (
            1.0
            if any(
                item.dst_ip == event.dst_ip
                for item in history_1h
                if event.dst_ip
            )
            else 0.0
        )

        historical_port_seen = (
            1.0
            if any(
                item.dst_port == event.dst_port
                for item in history_1h
                if event.dst_port > 0
            )
            else 0.0
        )

        current_failed_auth = (
            self._failed_auth(event)
        )

        result = {
            "behavior_events_1m": stats_1m["count"],
            "behavior_events_5m": stats_5m["count"],
            "behavior_events_1h": stats_1h["count"],
            "failed_auth_1m": stats_1m["failed_auth"],
            "failed_auth_5m": stats_5m["failed_auth"],
            "failed_auth_1h": stats_1h["failed_auth"],
            "unique_dst_ips_5m": stats_5m["unique_dst_ips"],
            "unique_dst_ports_5m": stats_5m["unique_dst_ports"],
            "unique_dst_ports_1h": stats_1h["unique_dst_ports"],
            "unique_users_5m": stats_5m["unique_users"],
            "http_4xx_rate_5m": http_4xx_rate,
            "http_5xx_rate_5m": http_5xx_rate,
            "bytes_out_5m": stats_5m["bytes_out"],
            "bytes_out_1h": stats_1h["bytes_out"],
            "request_burst_ratio": request_burst,
            "unique_port_rate": unique_port_rate,
            "seconds_since_previous": seconds_since_previous,
            "historical_destination_seen": historical_destination_seen,
            "historical_port_seen": historical_port_seen,
            "current_failed_auth": float(
                current_failed_auth
            ),
        }

        queue.append(
            HistoricalEvent(
                timestamp=event.timestamp,
                src_ip=event.src_ip,
                dst_ip=event.dst_ip,
                dst_port=event.dst_port,
                username=event.username,
                http_status=event.http_status,
                bytes_out=event.bytes_out,
                failed_auth=current_failed_auth,
            )
        )

        queue_sorted = sorted(
            queue,
            key=lambda item: item.timestamp,
        )

        queue.clear()
        queue.extend(queue_sorted)

        newest_historical_timestamp = max(
            (
                item.timestamp
                for item in queue
                if item.timestamp <= event.timestamp
            ),
            default=None,
        )

        if newest_historical_timestamp is not None:
            self.last_seen[key] = (
                newest_historical_timestamp
            )

        return result
