"""
Duplicate analysis for the three supplied UNSW-NB15 partitions.

Uses the same normalized-row fingerprint strategy as the ingestion layer
and distinguishes:
- duplicates within the same partition
- duplicates occurring across different partitions
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from collections import Counter
from pathlib import Path

from .deduplicator import Deduplicator
from .normalizer import normalize_row
from .reader import read_rows, row_to_mapping


def analyze(
    inputs: list[str | Path],
    database_path: str | Path,
) -> dict:
    database = Path(database_path)
    database.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(
        database
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS
        duplicate_analysis (
            row_hash TEXT PRIMARY KEY,
            first_file TEXT NOT NULL
        )
        """
    )

    connection.commit()

    total = 0
    unique = 0
    within_file = 0
    cross_file = 0

    per_file = Counter()
    cross_pairs = Counter()

    try:
        for input_file in inputs:
            source = Path(input_file)

            if not source.exists():
                raise FileNotFoundError(
                    f"UNSW file not found: {source}"
                )

            for _, raw_row in read_rows(source):
                total += 1
                per_file[source.name] += 1

                normalized = normalize_row(
                    row_to_mapping(raw_row)
                )

                digest = Deduplicator.fingerprint(
                    normalized
                )

                existing = connection.execute(
                    """
                    SELECT first_file
                    FROM duplicate_analysis
                    WHERE row_hash = ?
                    """,
                    (digest,),
                ).fetchone()

                if existing is None:
                    connection.execute(
                        """
                        INSERT INTO
                        duplicate_analysis(
                            row_hash,
                            first_file
                        )
                        VALUES (?, ?)
                        """,
                        (
                            digest,
                            source.name,
                        ),
                    )

                    unique += 1
                    continue

                first_file = existing[0]

                if first_file == source.name:
                    within_file += 1
                else:
                    cross_file += 1

                    pair = tuple(
                        sorted(
                            (
                                first_file,
                                source.name,
                            )
                        )
                    )

                    cross_pairs[
                        " <-> ".join(pair)
                    ] += 1

                if total % 10_000 == 0:
                    connection.commit()

        connection.commit()

    finally:
        connection.close()

    result = {
        "total_rows": total,
        "unique_rows": unique,
        "duplicate_rows": (
            within_file + cross_file
        ),
        "within_file_duplicates": within_file,
        "cross_file_duplicates": cross_file,
        "duplicate_rate": (
            (within_file + cross_file) / total
            if total
            else 0.0
        ),
        "rows_by_file": dict(per_file),
        "cross_file_pairs": dict(cross_pairs),
    }

    print(
        json.dumps(
            result,
            indent=2,
        )
    )

    return result


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--inputs",
        nargs="+",
        required=True,
    )

    parser.add_argument(
        "--database",
        default=(
            "data/processed/unsw_nb15/"
            "duplicate_analysis.sqlite3"
        ),
    )

    args = parser.parse_args()

    analyze(
        args.inputs,
        args.database,
    )


if __name__ == "__main__":
    main()
