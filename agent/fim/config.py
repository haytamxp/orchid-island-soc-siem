"""
Configuration for the FIM endpoint agent.

Configuration is provided through environment variables.

Examples:

PowerShell:

$env:FIM_SERVER_URL = "http://127.0.0.1:5001"
$env:FIM_AGENT_ID = "agt-win11-01"
$env:FIM_HOSTNAME = $env:COMPUTERNAME
$env:FIM_PATHS = "C:\Windows\System32\drivers\etc\hosts;C:\Windows\System32\drivers\etc\services"
"""

from __future__ import annotations

import os
import socket
from dataclasses import dataclass


@dataclass(frozen=True)
class FIMConfig:
    """
    Runtime configuration for the FIM agent.
    """

    server_url: str
    agent_id: str
    hostname: str
    monitored_paths: tuple[str, ...]
    debounce_seconds: float = 1.0
    request_timeout_seconds: float = 10.0

    @classmethod
    def from_environment(cls) -> "FIMConfig":
        server_url = os.getenv(
            "FIM_SERVER_URL",
            "http://127.0.0.1:5001",
        ).rstrip("/")

        agent_id = os.getenv(
            "FIM_AGENT_ID",
            socket.gethostname(),
        ).strip()

        hostname = os.getenv(
            "FIM_HOSTNAME",
            socket.gethostname(),
        ).strip()

        raw_paths = os.getenv(
            "FIM_PATHS",
            "",
        )

        monitored_paths = tuple(
            path.strip()
            for path in raw_paths.split(";")
            if path.strip()
        )

        debounce_seconds = _parse_float(
            os.getenv("FIM_DEBOUNCE_SECONDS"),
            default=1.0,
            minimum=0.0,
        )

        request_timeout_seconds = _parse_float(
            os.getenv("FIM_REQUEST_TIMEOUT_SECONDS"),
            default=10.0,
            minimum=1.0,
        )

        return cls(
            server_url=server_url,
            agent_id=agent_id,
            hostname=hostname,
            monitored_paths=monitored_paths,
            debounce_seconds=debounce_seconds,
            request_timeout_seconds=request_timeout_seconds,
        )


def _parse_float(
    value: str | None,
    default: float,
    minimum: float,
) -> float:
    """
    Safely parse a positive float.
    """

    if value is None:
        return default

    try:
        parsed = float(value)
    except ValueError:
        return default

    return max(minimum, parsed)