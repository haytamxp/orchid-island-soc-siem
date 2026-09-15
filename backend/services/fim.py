"""
FIM core logic.

Responsibilities:
- Calculate SHA-256 hashes.
- Collect file metadata.
- Classify FIM severity.
- Compare a file against a trusted baseline.
"""

from __future__ import annotations

import hashlib
import os
import platform
import stat
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class FileSnapshot:
    """
    Immutable representation of a file at a point in time.
    """

    path: str
    sha256: str
    size: int
    mode: Optional[str]
    owner: Optional[str]


@dataclass(frozen=True)
class FIMComparison:
    """
    Result of comparing a file against its trusted baseline.
    """

    exists: bool
    change_type: str
    old_hash: Optional[str]
    new_hash: Optional[str]
    old_size: Optional[int]
    new_size: Optional[int]
    severity: str


def sha256_file(path: str | os.PathLike[str], chunk_size: int = 1024 * 1024) -> str:
    """
    Calculate the SHA-256 digest of a file without loading it entirely
    into memory.
    """

    digest = hashlib.sha256()

    with open(path, "rb") as file_handle:
        while True:
            chunk = file_handle.read(chunk_size)
            if not chunk:
                break

            digest.update(chunk)

    return digest.hexdigest()


def _get_owner(path: str) -> Optional[str]:
    """
    Return a best-effort owner name.

    Linux/Unix:
        Resolve UID to a username.

    Windows:
        Keep this lightweight for the core implementation and return None.
        The Windows agent will provide richer identity information later.
    """

    try:
        file_stat = os.stat(path)

        if platform.system().lower() == "windows":
            return None

        import pwd

        return pwd.getpwuid(file_stat.st_uid).pw_name
    except (OSError, KeyError, ImportError):
        return None


def _get_mode(path: str) -> Optional[str]:
    """
    Return a normalized permission representation.
    """

    try:
        file_stat = os.stat(path)
        return stat.filemode(file_stat.st_mode)
    except OSError:
        return None


def snapshot_file(path: str | os.PathLike[str]) -> FileSnapshot:
    """
    Build a trusted snapshot from the current file contents and metadata.
    """

    normalized_path = str(Path(path).resolve())

    if not os.path.isfile(normalized_path):
        raise FileNotFoundError(normalized_path)

    file_stat = os.stat(normalized_path)

    return FileSnapshot(
        path=normalized_path,
        sha256=sha256_file(normalized_path),
        size=file_stat.st_size,
        mode=_get_mode(normalized_path),
        owner=_get_owner(normalized_path),
    )


def severity_for_path(path: str, change_type: str) -> str:
    """
    Assign severity according to the sensitivity of a monitored path.

    This is intentionally deterministic. More advanced risk scoring can
    be layered later without changing the core integrity mechanism.
    """

    normalized = path.replace("\\", "/").lower()

    critical_exact = {
        "/etc/shadow",
        "/etc/sudoers",
        "/etc/sudoers.d",
        "/etc/passwd",
        "/boot/grub/grub.cfg",
    }

    high_prefixes = (
        "/etc/ssh/",
        "/etc/systemd/",
        "/etc/nginx/",
        "/etc/apache2/",
        "/var/www/",
        "/etc/security/",
        "/etc/pam.d/",
        "c:/windows/system32/config/",
        "c:/windows/system32/drivers/etc/",
        "c:/windows/system32/tasks/",
    )

    critical_windows_prefixes = (
        "c:/windows/system32/",
    )

    if normalized in critical_exact:
        return "Critical"

    if any(normalized.startswith(prefix) for prefix in critical_windows_prefixes):
        return "Critical"

    if any(normalized.startswith(prefix) for prefix in high_prefixes):
        return "High"

    if change_type == "deleted":
        return "High"

    if change_type == "added":
        return "Medium"

    return "Medium"


def compare_snapshot(
    baseline_hash: Optional[str],
    baseline_size: Optional[int],
    current: Optional[FileSnapshot],
    path: str,
) -> FIMComparison:
    """
    Compare a current snapshot with a trusted baseline.
    """

    if current is None:
        return FIMComparison(
            exists=False,
            change_type="deleted",
            old_hash=baseline_hash,
            new_hash=None,
            old_size=baseline_size,
            new_size=None,
            severity=severity_for_path(path, "deleted"),
        )

    if baseline_hash is None:
        return FIMComparison(
            exists=True,
            change_type="added",
            old_hash=None,
            new_hash=current.sha256,
            old_size=None,
            new_size=current.size,
            severity=severity_for_path(path, "added"),
        )

    if current.sha256 != baseline_hash:
        return FIMComparison(
            exists=True,
            change_type="modified",
            old_hash=baseline_hash,
            new_hash=current.sha256,
            old_size=baseline_size,
            new_size=current.size,
            severity=severity_for_path(path, "modified"),
        )

    return FIMComparison(
        exists=True,
        change_type="unchanged",
        old_hash=baseline_hash,
        new_hash=current.sha256,
        old_size=baseline_size,
        new_size=current.size,
        severity="Low",
    )


def snapshot_to_dict(snapshot: FileSnapshot) -> dict:
    """
    Serialize a FileSnapshot for persistence/API responses.
    """

    return {
        "path": snapshot.path,
        "sha256": snapshot.sha256,
        "size": snapshot.size,
        "mode": snapshot.mode,
        "owner": snapshot.owner,
    }