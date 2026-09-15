"""
Remote baseline cache for the FIM agent.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

import requests


LOGGER = logging.getLogger("fim.baseline")


@dataclass(frozen=True)
class Baseline:
    """
    Trusted state of one monitored file.
    """

    file_path: str
    sha256: str
    file_size: int


class BaselineCache:
    """
    Loads the server-side FIM baselines and keeps them in memory.

    Baselines are intentionally NOT modified automatically when a change
    is detected. This prevents an attacker from turning an unauthorized
    modification into the new trusted state.
    """

    def __init__(
        self,
        server_url: str,
        hostname: str,
        timeout: float = 10.0,
    ) -> None:
        self.server_url = server_url.rstrip("/")
        self.hostname = hostname
        self.timeout = timeout

        self._baselines: dict[str, Baseline] = {}

        self.session = requests.Session()

    def load(self) -> None:
        """
        Retrieve all active baselines for this hostname.
        """

        url = f"{self.server_url}/api/fim/baselines"

        response = self.session.get(
            url,
            params={
                "hostname": self.hostname,
            },
            timeout=self.timeout,
        )

        response.raise_for_status()

        data = response.json()

        if not isinstance(data, list):
            raise ValueError(
                "FIM baseline API returned an invalid response"
            )

        self._baselines.clear()

        for item in data:
            file_path = item.get("file_path")
            sha256 = item.get("sha256")
            file_size = item.get("file_size")

            if not file_path or not sha256:
                continue

            try:
                normalized_size = int(file_size or 0)
            except (TypeError, ValueError):
                normalized_size = 0

            self._baselines[file_path] = Baseline(
                file_path=file_path,
                sha256=sha256,
                file_size=normalized_size,
            )

        LOGGER.info(
            "Loaded %d FIM baselines for %s",
            len(self._baselines),
            self.hostname,
        )

    def get(
        self,
        file_path: str,
    ) -> Optional[Baseline]:
        """
        Return the trusted baseline for a file.
        """

        return self._baselines.get(file_path)

    def contains(
        self,
        file_path: str,
    ) -> bool:
        """
        Return whether a file has a trusted baseline.
        """

        return file_path in self._baselines