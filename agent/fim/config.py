"""
Configuration for the Windows FIM agent.
"""

from __future__ import annotations

import os
import socket
from dataclasses import dataclass


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)

    if value is None:
        return default

    try:
        return int(value)
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)

    if value is None:
        return default

    try:
        return float(value)
    except ValueError:
        return default


@dataclass(frozen=True)
class FIMConfig:
    server_url: str
    hostname: str
    agent_id: str
    paths: tuple[str, ...]
    debounce_seconds: float
    request_timeout_seconds: int
    register_baselines: bool


def load_config() -> FIMConfig:
    server_url = os.getenv(
        "FIM_SERVER_URL",
        "http://127.0.0.1:5001",
    ).rstrip("/")

    hostname = os.getenv(
        "FIM_HOSTNAME",
        socket.gethostname(),
    )

    agent_id = os.getenv(
        "FIM_AGENT_ID",
        f"fim-{hostname}",
    )

    raw_paths = os.getenv(
        "FIM_PATHS",
        r"C:\Windows\System32\drivers\etc\hosts",
    )

    paths = tuple(
        os.path.abspath(path.strip())
        for path in raw_paths.split(";")
        if path.strip()
    )

    return FIMConfig(
        server_url=server_url,
        hostname=hostname,
        agent_id=agent_id,
        paths=paths,
        debounce_seconds=_env_float(
            "FIM_DEBOUNCE_SECONDS",
            1.0,
        ),
        request_timeout_seconds=_env_int(
            "FIM_REQUEST_TIMEOUT_SECONDS",
            10,
        ),
        register_baselines=os.getenv(
            "FIM_REGISTER_BASELINES",
            "true",
        ).lower() in {
            "1",
            "true",
            "yes",
            "on",
        },
    )