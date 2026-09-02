"""
End-to-end streaming UNSW-NB15 cleaner.
"""

from __future__ import annotations

import csv
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from .deduplicator import Deduplicator
from .normalizer import normalize_row
from .reader import read_rows, row_to_mapping
from .schema import SCHEMA
from .validator import validate_row


OUTPUT_COLUMNS = [
    *SCHEMA,
    "dataset_source",
    "source_file",
    "start_time",
    "end_time",
]


def unix_to_iso(
    value: int | None,
) -> str | None:
    if value is None:
        return None

    try:
        return datetime.fromtimestamp(
            value,
            tz=timezone.utc,
        ).isoformat()
    except (OverflowError, OSError, ValueError):
        return None


def clean_files(
    inputs: Iterable[str | Path],
    output: str | Path,
    duplicate_db: str | Path,
    error_output: str | Path | None = None,
    commit_every: int = 10000,
) -> dict[str, Any]:

    output_path = Path(output)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if error_output is None:
        error_path = output_path.with_name(
            output_path.stem
            + "_errors.csv"
        )
    else:
        error_path = Path(
            error_output
        )

    error_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    deduplicator = Deduplicator(
        duplicate_db
    )

    stats = {
        "input_rows": 0,
        "accepted_rows": 0,
        "duplicate_rows": 0,
        "invalid_rows": 0,
        "files": Counter(),
        "labels": Counter(),
        "attack_categories": Counter(),
        "errors": Counter(),
    }

    output_exists = (
        output_path.exists()
        and output_path.stat().st_size > 0
    )

    error_exists = (
        error_path.exists()
        and error_path.stat().st_size > 0
    )

    try:
        with output_path.open(
            "a",
            encoding="utf-8",
            newline="",
        ) as output_handle, error_path.open(
            "a",
            encoding="utf-8",
            newline="",
        ) as error_handle:

            writer = csv.DictWriter(
                output_handle,
                fieldnames=OUTPUT_COLUMNS,
            )

            error_writer = csv.DictWriter(
                error_handle,
                fieldnames=[
                    "source_file",
                    "line_number",
                    "reason",
                ],
            )

            if not output_exists:
                writer.writeheader()

            if not error_exists:
                error_writer.writeheader()

            for input_file in inputs:
                source = Path(
                    input_file
                )

                for line_number, raw_row in read_rows(
                    source
                ):
                    stats["input_rows"] += 1
                    stats["files"][
                        source.name
                    ] += 1

                    try:
                        mapping = row_to_mapping(
                            raw_row
                        )

                        normalized = normalize_row(
                            mapping
                        )

                        errors = validate_row(
                            normalized
                        )

                        if errors:
                            raise ValueError(
                                "; ".join(errors)
                            )

                        if not deduplicator.is_new(
                            normalized
                        ):
                            stats[
                                "duplicate_rows"
                            ] += 1

                            continue

                        record = dict(
                            normalized
                        )

                        record[
                            "dataset_source"
                        ] = "unsw_nb15"

                        record[
                            "source_file"
                        ] = source.name

                        record[
                            "start_time"
                        ] = unix_to_iso(
                            normalized.get(
                                "stime"
                            )
                        )

                        record[
                            "end_time"
                        ] = unix_to_iso(
                            normalized.get(
                                "ltime"
                            )
                        )

                        writer.writerow(
                            record
                        )

                        stats[
                            "accepted_rows"
                        ] += 1

                        stats["labels"][
                            str(
                                normalized[
                                    "label"
                                ]
                            )
                        ] += 1

                        category = (
                            normalized.get(
                                "attack_cat"
                            )
                        )

                        stats[
                            "attack_categories"
                        ][
                            category or "__MISSING__"
                        ] += 1

                        if (
                            stats["accepted_rows"]
                            % commit_every
                            == 0
                        ):
                            deduplicator.commit()
                            output_handle.flush()

                    except Exception as exc:
                        stats[
                            "invalid_rows"
                        ] += 1

                        reason = str(
                            exc
                        )

                        error_writer.writerow(
                            {
                                "source_file": (
                                    source.name
                                ),
                                "line_number": (
                                    line_number
                                ),
                                "reason": reason,
                            }
                        )

                        stats[
                            "errors"
                        ][
                            reason
                        ] += 1

        deduplicator.commit()

    finally:
        deduplicator.close()

    stats["files"] = dict(
        stats["files"]
    )

    stats["labels"] = dict(
        stats["labels"]
    )

    stats[
        "attack_categories"
    ] = dict(
        stats["attack_categories"]
    )

    stats["errors"] = dict(
        stats["errors"]
    )

    total = stats[
        "input_rows"
    ]

    stats[
        "acceptance_rate"
    ] = (
        stats["accepted_rows"] / total
        if total
        else 0.0
    )

    stats[
        "duplicate_rate"
    ] = (
        stats["duplicate_rows"] / total
        if total
        else 0.0
    )

    stats[
        "invalid_rate"
    ] = (
        stats["invalid_rows"] / total
        if total
        else 0.0
    )

    print(
        "=== UNSW-NB15 Cleaning Report ==="
    )

    print(
        f"Input rows: "
        f"{stats['input_rows']}"
    )

    print(
        f"Accepted rows: "
        f"{stats['accepted_rows']}"
    )

    print(
        f"Duplicate rows: "
        f"{stats['duplicate_rows']}"
    )

    print(
        f"Invalid rows: "
        f"{stats['invalid_rows']}"
    )

    print(
        f"Acceptance rate: "
        f"{stats['acceptance_rate']:.2%}"
    )

    print(
        f"Duplicate rate: "
        f"{stats['duplicate_rate']:.2%}"
    )

    print(
        f"Invalid rate: "
        f"{stats['invalid_rate']:.2%}"
    )

    print(
        f"Labels: "
        f"{stats['labels']}"
    )

    print(
        "Attack categories:"
    )

    for category, count in sorted(
        stats["attack_categories"].items()
    ):
        print(
            f"  {category}: {count}"
        )

    print(
        f"Output: {output_path}"
    )

    print(
        f"Rejected rows: {error_path}"
    )

    return stats
