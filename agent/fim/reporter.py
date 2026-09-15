"""
HTTP reporter for the FIM agent.
"""

from __future__ import annotations

import logging
from typing import Optional

import requests


LOGGER = logging.getLogger("fim.reporter")


class FIMReporter:
    """
    Sends FIM events to the Flask backend.
    """

    def __init__(
        self,
        server_url: str,
        hostname: str,
        agent_id: str,
        timeout: float = 10.0,
    ) -> None:
        self.server_url = server_url.rstrip("/")
        self.hostname = hostname
        self.agent_id = agent_id
        self.timeout = timeout

        self.session = requests.Session()

    @property
    def events_url(self) -> str:
        return f"{self.server_url}/api/fim/events"

    def report(
        self,
        *,
        file_path: str,
        change_type: str,
        old_hash: Optional[str],
        new_hash: Optional[str],
        old_size: Optional[int],
        new_size: Optional[int],
        severity: str,
        actor: Optional[str] = None,
        process_name: Optional[str] = None,
        details: Optional[str] = None,
    ) -> bool:
        """
        Send one FIM event to the backend.

        Returns True on HTTP success, False otherwise.
        """

        payload = {
            "hostname": self.hostname,
            "file_path": file_path,
            "change_type": change_type,
            "old_hash": old_hash,
            "new_hash": new_hash,
            "old_size": old_size,
            "new_size": new_size,
            "severity": severity,
            "actor": actor,
            "process_name": process_name,
            "agent_id": self.agent_id,
            "details": details,
        }

        try:
            response = self.session.post(
                self.events_url,
                json=payload,
                timeout=self.timeout,
            )

            response.raise_for_status()

            LOGGER.info(
                "FIM event reported: %s [%s]",
                file_path,
                change_type,
            )

            return True

        except requests.RequestException as exc:
            LOGGER.error(
                "Failed to report FIM event for %s: %s",
                file_path,
                exc,
            )
            return False