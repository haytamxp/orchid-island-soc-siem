"""
UNSW-NB15 value normalization.
"""

from __future__ import annotations

import math
from typing import Any

from .schema import (
    CATEGORICAL_COLUMNS,
    FLOAT_COLUMNS,
    INTEGER_COLUMNS,
)


ATTACK_ALIASES = {
    "backdoor": "Backdoors",
    "backdoors": "Backdoors",
    "fuzzer": "Fuzzers",
    "fuzzers": "Fuzzers",
    "reconnaissance": "Reconnaissance",
    "shellcode": "Shellcode",
    "exploits": "Exploits",
    "analysis": "Analysis",
    "dos": "DoS",
    "generic": "Generic",
    "worms": "Worms",
}


def clean_text(
    value: Any,
) -> str | None:
    if value is None:
        return None

    text = str(value).strip()

    if text in {
        "",
        "-",
        "NaN",
        "nan",
        "None",
        "none",
    }:
        return None

    return text


def normalize_attack_category(
    value: Any,
) -> str | None:
    cleaned = clean_text(value)

    if cleaned is None:
        return None

    return ATTACK_ALIASES.get(
        cleaned.lower(),
        cleaned,
    )


def normalize_integer(
    value: Any,
) -> int | None:
    cleaned = clean_text(value)

    if cleaned is None:
        return None

    try:
        numeric = float(cleaned)
    except (TypeError, ValueError):
        raise ValueError(
            f"invalid integer value: {value!r}"
        )

    if not math.isfinite(numeric):
        raise ValueError(
            f"non-finite integer value: {value!r}"
        )

    if not numeric.is_integer():
        raise ValueError(
            f"non-integer numeric value: {value!r}"
        )

    return int(numeric)


def normalize_float(
    value: Any,
) -> float | None:
    cleaned = clean_text(value)

    if cleaned is None:
        return None

    try:
        numeric = float(cleaned)
    except (TypeError, ValueError):
        raise ValueError(
            f"invalid float value: {value!r}"
        )

    if not math.isfinite(numeric):
        raise ValueError(
            f"non-finite float value: {value!r}"
        )

    return numeric


def normalize_row(
    row: dict[str, str],
) -> dict[str, Any]:
    result: dict[str, Any] = {}

    for column, value in row.items():
        if column in CATEGORICAL_COLUMNS:
            if column == "attack_cat":
                result[column] = (
                    normalize_attack_category(
                        value
                    )
                )
            else:
                result[column] = clean_text(
                    value
                )

        elif column in INTEGER_COLUMNS:
            result[column] = normalize_integer(
                value
            )

        elif column in FLOAT_COLUMNS:
            result[column] = normalize_float(
                value
            )

        elif column in {
            "srcip",
            "dstip",
        }:
            result[column] = clean_text(
                value
            )

        else:
            result[column] = clean_text(
                value
            )

    if result.get("label") is not None:
        if result["label"] not in (0, 1):
            raise ValueError(
                f"label must be 0 or 1, "
                f"got {result['label']!r}"
            )

    return result
