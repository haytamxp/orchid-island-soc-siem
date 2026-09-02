"""
Persistent global duplicate detection using SQLite + SHA-256.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any


class Deduplicator:
    def __init__(
        self,
        database_path: str | Path,
    ) -> None:
        self.path = Path(
            database_path
        )

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.connection = sqlite3.connect(
            self.path
        )

        self.connection.execute(
            """
            PRAGMA journal_mode=WAL
            """
        )

        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS seen_rows (
                row_hash TEXT PRIMARY KEY
            )
            """
        )

        self.connection.commit()

    @staticmethod
    def fingerprint(
        row: dict[str, Any],
    ) -> str:
        payload = json.dumps(
            row,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            default=str,
        )

        return hashlib.sha256(
            payload.encode("utf-8")
        ).hexdigest()

    def is_new(
        self,
        row: dict[str, Any],
    ) -> bool:
        digest = self.fingerprint(
            row
        )

        cursor = self.connection.execute(
            """
            INSERT OR IGNORE
            INTO seen_rows(row_hash)
            VALUES (?)
            """,
            (digest,),
        )

        return cursor.rowcount == 1

    def commit(self) -> None:
        self.connection.commit()

    def close(self) -> None:
        try:
            self.connection.commit()
        finally:
            self.connection.close()
