"""
Validation and normalization for FIM API payloads.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any


ALLOWED_CHANGE_TYPES = {
    "added",
    "modified",
    "deleted",
}

ALLOWED_SEVERITIES = {
    "Low",
    "Medium",
    "High",
    "Critical",
}


def _clean_string(
    value: Any,
    field: str,
    max_length: int,
    required: bool = True,
) -> str | None:
    """
    Normalize a string API field.
    """

    if value is None:
        if required:
            raise ValueError(f"{field} is required")

        return None

    if not isinstance(value, str):
        raise ValueError(f"{field} must be a string")

    value = value.strip()

    if required and not value:
        raise ValueError(f"{field} cannot be empty")

    if len(value) > max_length:
        raise ValueError(
            f"{field} exceeds the maximum length of {max_length}"
        )

    return value


def normalize_baseline_payload(payload: dict) -> dict:
    """
    Validate a baseline creation request.
    """

    if not isinstance(payload, dict):
        raise ValueError("JSON body must be an object")

    hostname = _clean_string(
        payload.get("hostname"),
        "hostname",
        255,
    )

    file_path = _clean_string(
        payload.get("file_path"),
        "file_path",
        1000,
    )

    normalized_path = str(
        Path(file_path).expanduser()
    )

    if not os.path.isabs(normalized_path):
        raise ValueError("file_path must be an absolute path")

    return {
        "hostname": hostname,
        "file_path": normalized_path,
    }


def normalize_event_payload(payload: dict) -> dict:
    """
    Validate an externally generated FIM event.

    This endpoint is intended primarily for agents.
    """

    if not isinstance(payload, dict):
        raise ValueError("JSON body must be an object")

    hostname = _clean_string(
        payload.get("hostname"),
        "hostname",
        255,
    )

    file_path = _clean_string(
        payload.get("file_path"),
        "file_path",
        1000,
    )

    change_type = _clean_string(
        payload.get("change_type"),
        "change_type",
        50,
    )

    if change_type not in ALLOWED_CHANGE_TYPES:
        raise ValueError(
            f"change_type must be one of: "
            f"{', '.join(sorted(ALLOWED_CHANGE_TYPES))}"
        )

    severity = payload.get("severity", "Medium")

    if severity not in ALLOWED_SEVERITIES:
        raise ValueError(
            f"severity must be one of: "
            f"{', '.join(sorted(ALLOWED_SEVERITIES))}"
        )

    return {
        "hostname": hostname,
        "file_path": file_path,
        "change_type": change_type,
        "old_hash": payload.get("old_hash"),
        "new_hash": payload.get("new_hash"),
        "old_size": payload.get("old_size"),
        "new_size": payload.get("new_size"),
        "severity": severity,
        "actor": _clean_string(
            payload.get("actor"),
            "actor",
            255,
            required=False,
        ),
        "process_name": _clean_string(
            payload.get("process_name"),
            "process_name",
            255,
            required=False,
        ),
        "agent_id": _clean_string(
            payload.get("agent_id"),
            "agent_id",
            100,
            required=False,
        ),
        "details": _clean_string(
            payload.get("details"),
            "details",
            5000,
            required=False,
        ),
    }


def normalize_limit(value: Any) -> int:
    """
    Normalize the API limit parameter.
    """

    try:
        limit = int(value)
    except (TypeError, ValueError):
        return 200

    return max(1, min(limit, 1000))