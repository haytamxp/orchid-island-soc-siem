"""
Canonical security event schema for Orchid Island SOC/SIEM.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Mapping, Optional


def _text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def _int(value: Any, default: int = 0) -> int:
    if value in (None, ""):
        return default
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _float(value: Any, default: float = 0.0) -> float:
    if value in (None, ""):
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def parse_timestamp(value: Any) -> datetime:
    if isinstance(value, datetime):
        dt = value
    else:
        raw = _text(value)

        if not raw:
            return datetime.now(timezone.utc)

        if raw.endswith("Z"):
            raw = raw[:-1] + "+00:00"

        try:
            dt = datetime.fromisoformat(raw)
        except ValueError:
            try:
                dt = datetime.strptime(
                    raw,
                    "%Y-%m-%d %H:%M:%S",
                )
            except ValueError:
                return datetime.now(timezone.utc)

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt.astimezone(timezone.utc)


@dataclass(slots=True)
class CanonicalEvent:
    timestamp: datetime
    severity: str
    source: str
    category: str
    description: str
    src_ip: str
    dst_ip: str
    dst_port: int
    username: str
    hostname: str
    url: str
    http_method: str
    http_status: int
    bytes_in: float = 0.0
    bytes_out: float = 0.0
    action: str = ""
    event_id: str = ""
    label: Optional[int] = None

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "CanonicalEvent":
        def pick(*names: str) -> Any:
            for name in names:
                if name in data and data[name] not in (None, ""):
                    return data[name]
            return None

        raw_label = pick(
            "label",
            "target",
            "is_malicious",
        )

        label: Optional[int]

        if raw_label in (None, ""):
            label = None
        else:
            try:
                label = int(float(raw_label))
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"Invalid binary label: {raw_label!r}"
                ) from exc

            if label not in (0, 1):
                raise ValueError(
                    f"Label must be 0 or 1, got {label}"
                )

        return cls(
            timestamp=parse_timestamp(
                pick(
                    "timestamp",
                    "@timestamp",
                    "time",
                    "datetime",
                )
            ),
            severity=_text(
                pick("severity", "level")
            ).lower(),
            source=_text(
                pick("source", "sensor", "collector")
            ).lower(),
            category=_text(
                pick(
                    "category",
                    "event_type",
                    "type",
                )
            ).lower(),
            description=_text(
                pick(
                    "description",
                    "message",
                    "msg",
                    "event_description",
                )
            ),
            src_ip=_text(
                pick(
                    "src_ip",
                    "source_ip",
                    "srcip",
                    "client_ip",
                )
            ),
            dst_ip=_text(
                pick(
                    "dst_ip",
                    "destination_ip",
                    "dstip",
                    "server_ip",
                )
            ),
            dst_port=_int(
                pick(
                    "dst_port",
                    "destination_port",
                    "dest_port",
                )
            ),
            username=_text(
                pick(
                    "username",
                    "user",
                    "user_name",
                )
            ),
            hostname=_text(
                pick(
                    "hostname",
                    "host",
                    "agent",
                )
            ),
            url=_text(
                pick(
                    "url",
                    "uri",
                    "request_uri",
                    "http_url",
                )
            ),
            http_method=_text(
                pick(
                    "http_method",
                    "method",
                )
            ).upper(),
            http_status=_int(
                pick(
                    "http_status",
                    "status_code",
                    "response_code",
                )
            ),
            bytes_in=_float(
                pick(
                    "bytes_in",
                    "in_bytes",
                    "network_bytes_in",
                )
            ),
            bytes_out=_float(
                pick(
                    "bytes_out",
                    "out_bytes",
                    "network_bytes_out",
                )
            ),
            action=_text(
                pick(
                    "action",
                    "outcome",
                    "auth_action",
                )
            ).lower(),
            event_id=_text(
                pick(
                    "event_id",
                    "id",
                    "uid",
                )
            ),
            label=label,
        )

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["timestamp"] = self.timestamp.isoformat()
        return result
