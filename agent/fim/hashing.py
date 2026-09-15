"""
File hashing and local snapshot collection for the FIM agent.
"""

from __future__ import annotations

import getpass
import hashlib
import os
import stat
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class FileSnapshot:
    path: str
    sha256: str
    size: int
    mode: str | None
    owner_name: str | None


def sha256_file(
    path: str,
    chunk_size: int = 1024 * 1024,
) -> str:
    """Calculate SHA-256 without loading the entire file."""

    digest = hashlib.sha256()

    with open(path, "rb") as file_handle:
        while True:
            chunk = file_handle.read(chunk_size)

            if not chunk:
                break

            digest.update(chunk)

    return digest.hexdigest()


def snapshot_file(path: str) -> FileSnapshot:
    """Capture the current state of a file."""

    normalized_path = str(
        Path(path).resolve()
    )

    if not os.path.isfile(normalized_path):
        raise FileNotFoundError(
            normalized_path
        )

    file_stat = os.stat(
        normalized_path
    )

    try:
        mode = stat.filemode(
            file_stat.st_mode
        )
    except (OSError, ValueError):
        mode = None

    try:
        owner_name = getpass.getuser()
    except Exception:
        owner_name = None

    return FileSnapshot(
        path=normalized_path,
        sha256=sha256_file(
            normalized_path
        ),
        size=file_stat.st_size,
        mode=mode,
        owner_name=owner_name,
    )


def snapshot_to_dict(
    snapshot: FileSnapshot,
) -> dict:
    return asdict(snapshot)