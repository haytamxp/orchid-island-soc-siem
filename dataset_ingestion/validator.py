"""
Row-level UNSW-NB15 validation.
"""

from __future__ import annotations

import ipaddress
from typing import Any

from .schema import (
    REQUIRED_COLUMNS,
    SCHEMA,
)


def validate_row(
    row: dict[str, Any],
) -> list[str]:
    errors: list[str] = []

    missing_required = [
        column
        for column in REQUIRED_COLUMNS
        if row.get(column) is None
    ]

    if missing_required:
        errors.append(
            "missing required fields: "
            + ", ".join(
                sorted(missing_required)
            )
        )

    for column in (
        "srcip",
        "dstip",
    ):
        value = row.get(column)

        if value is None:
            continue

        try:
            ipaddress.ip_address(
                str(value)
            )
        except ValueError:
            errors.append(
                f"invalid {column}: {value!r}"
            )

    sport = row.get("sport")

    if sport is not None and not (
        0 <= sport <= 65535
    ):
        errors.append(
            f"invalid sport: {sport}"
        )

    dsport = row.get("dsport")

    if dsport is not None and not (
        0 <= dsport <= 65535
    ):
        errors.append(
            f"invalid dsport: {dsport}"
        )

    label = row.get("label")

    if label not in (0, 1):
        errors.append(
            f"invalid label: {label!r}"
        )

    if len(row) != len(SCHEMA):
        errors.append(
            "normalized row schema mismatch"
        )

    duration = row.get("dur")

    if duration is not None and duration < 0:
        errors.append(
            f"negative duration: {duration}"
        )

    stime = row.get("stime")
    ltime = row.get("ltime")

    if (
        stime is not None
        and ltime is not None
        and ltime < stime
    ):
        errors.append(
            "ltime earlier than stime"
        )

    return errors
