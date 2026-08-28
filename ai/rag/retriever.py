"""
Classification-based SOC playbook retriever.

The retriever maps validated AI classifications to trusted local
remediation playbooks.

Only predefined filenames from CLASSIFICATION_TO_PLAYBOOK can be
loaded. No user-controlled filesystem path is accepted.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


PLAYBOOKS_DIR = (
    Path(__file__).resolve().parent / "playbooks"
)


CLASSIFICATION_TO_PLAYBOOK: dict[str, str] = {
    "SQL_INJECTION": "playbook_sqli.md",
    "XSS": "playbook_xss.md",
    "BRUTE_FORCE": "playbook_bruteforce.md",
    "CSRF": "playbook_csrf.md",
    "PATH_TRAVERSAL": "playbook_path_traversal.md",
    "MALWARE": "playbook_malware.md",
    "CREDENTIAL_ATTACK": "playbook_credential_attack.md",
    "SCANNING": "playbook_scanning.md",
}


def get_playbook(
    classification: Any,
) -> str | None:
    """
    Return the remediation playbook for a classification.

    Supported inputs:
    - a string such as "SQL_INJECTION";
    - an Enum instance such as Classification.SQL_INJECTION.

    Returns:
        The Markdown playbook content, or None when no
        playbook is mapped or the file does not exist.
    """

    classification_value = getattr(
        classification,
        "value",
        classification,
    )

    if not isinstance(
        classification_value,
        str,
    ):
        return None

    filename = CLASSIFICATION_TO_PLAYBOOK.get(
        classification_value.upper()
    )

    if not filename:
        return None

    path = PLAYBOOKS_DIR / filename

    if not path.is_file():
        return None

    return path.read_text(
        encoding="utf-8"
    )