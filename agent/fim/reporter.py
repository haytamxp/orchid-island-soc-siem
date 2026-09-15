"""
HTTP reporter for the Windows FIM agent.
"""

from __future__ import annotations

from typing import Any

import requests

from agent.fim.config import FIMConfig
from agent.fim.hashing import FileSnapshot


def _normalize_path(path: str) -> str:
    return path.replace("\\", "/").lower()


def _severity_for_path(
    path: str,
    change_type: str,
) -> str:
    normalized = _normalize_path(path)

    critical_prefixes = (
        "c:/windows/system32/",
    )

    high_prefixes = (
        "c:/windows/system32/config/",
        "c:/windows/system32/drivers/etc/",
        "c:/windows/system32/tasks/",
        "c:/windows/system32/winlogon/",
        "c:/windows/system32/group policy/",
    )

    if any(
        normalized.startswith(prefix)
        for prefix in critical_prefixes
    ):
        return "Critical"

    if any(
        normalized.startswith(prefix)
        for prefix in high_prefixes
    ):
        return "High"

    if change_type == "deleted":
        return "High"

    return "Medium"


class FIMReporter:
    """Send real FIM telemetry to Flask."""

    def __init__(
        self,
        config: FIMConfig,
    ) -> None:
        self.config = config

        self.session = requests.Session()

        self.session.headers.update(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": (
                    f"OrchidIsland-FIM/{config.agent_id}"
                ),
            }
        )

    def _post(
        self,
        endpoint: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        url = (
            f"{self.config.server_url}"
            f"/api/fim/{endpoint}"
        )

        response = self.session.post(
            url,
            json=payload,
            timeout=self.config.request_timeout_seconds,
        )

        response.raise_for_status()

        data = response.json()

        if not isinstance(data, dict):
            raise RuntimeError(
                f"Unexpected response from {url}"
            )

        return data

    def register_baseline(
        self,
        snapshot: FileSnapshot,
    ) -> dict[str, Any]:
        payload = {
            "hostname": self.config.hostname,
            "file_path": snapshot.path,
            "sha256": snapshot.sha256,
            "file_size": snapshot.size,
            "mode": snapshot.mode,
            "owner_name": snapshot.owner_name,
            "agent_id": self.config.agent_id,
        }

        return self._post(
            "baselines",
            payload,
        )

    def report_event(
        self,
        snapshot: FileSnapshot | None,
        old_hash: str | None,
        old_size: int | None,
        file_path: str,
        change_type: str,
        details: str,
    ) -> dict[str, Any]:
        new_hash = (
            snapshot.sha256
            if snapshot is not None
            else None
        )

        new_size = (
            snapshot.size
            if snapshot is not None
            else None
        )

        payload = {
            "hostname": self.config.hostname,
            "file_path": file_path,
            "change_type": change_type,
            "old_hash": old_hash,
            "new_hash": new_hash,
            "old_size": old_size,
            "new_size": new_size,
            "severity": _severity_for_path(
                file_path,
                change_type,
            ),
            "actor": None,
            "process_name": None,
            "agent_id": self.config.agent_id,
            "details": details,
        }

        return self._post(
            "events",
            payload,
        )

    def get_baselines(
        self,
    ) -> list[dict[str, Any]]:
        url = (
            f"{self.config.server_url}"
            "/api/fim/baselines"
        )

        response = self.session.get(
            url,
            params={
                "hostname": self.config.hostname,
            },
            timeout=self.config.request_timeout_seconds,
        )

        response.raise_for_status()

        data = response.json()

        if not isinstance(data, list):
            raise RuntimeError(
                "Unexpected baseline response."
            )

        return data