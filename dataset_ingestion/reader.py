"""
Streaming reader for headerless UNSW-NB15 CSV files.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterator

from .schema import SCHEMA


def read_rows(
    path: str | Path,
) -> Iterator[tuple[int, list[str]]]:
    """
    Yield (line_number, row) without loading the complete file.

    UNSW-NB15 partitions are headerless.
    """

    source = Path(path)

    if not source.exists():
        raise FileNotFoundError(
            f"UNSW file not found: {source}"
        )

    with source.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        reader = csv.reader(handle)

        for line_number, row in enumerate(
            reader,
            start=1,
        ):
            yield line_number, row


def row_to_mapping(
    row: list[str],
) -> dict[str, str]:
    if len(row) != len(SCHEMA):
        raise ValueError(
            f"Expected {len(SCHEMA)} columns, "
            f"got {len(row)}"
        )

    return dict(
        zip(
            SCHEMA,
            row,
        )
    )
