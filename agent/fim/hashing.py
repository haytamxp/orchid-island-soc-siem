"""
File hashing and snapshot helpers for the FIM agent.
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class FileSnapshot:
    """
    Point-in-time file state.
    """

    path: str
    sha256: str
    size: int


def calculate_sha256(
    path: str,
    chunk_size: int = 1024 * 1024,
) -> str:
    """
    Calculate SHA-256 incrementally.

    Incremental reads prevent large monitored files from being loaded
    completely into memory.
    """

    digest = hashlib.sha256()

    with open(path, "rb") as file_handle:
        while True:
            chunk = file_handle.read(chunk_size)

            if not chunk:
                break

            digest.update(chunk)

    return digest.hexdigest()


def snapshot_file(path: str) -> Optional[FileSnapshot]:
    """
    Safely create a snapshot of an existing regular file.

    Returns None when the file disappears during the operation.
    """

    normalized_path = str(
        Path(path).expanduser().resolve()
    )

    try:
        if not os.path.isfile(normalized_path):
            return None

        file_size = os.path.getsize(normalized_path)
        file_hash = calculate_sha256(normalized_path)

        return FileSnapshot(
            path=normalized_path,
            sha256=file_hash,
            size=file_size,
        )

    except (FileNotFoundError, PermissionError, OSError):
        return None