"""
Simple classification-based playbook retriever.

The retriever maps a validated AI classification to a local
security remediation playbook.

Only filenames from the fixed allow-list below can be opened.
No user-supplied filesystem path is accepted.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


PLAYBOOKS_DIR = Path(__file__).resolve().parent / "playbooks"


CLASSIFICATION_TO_PLAYBOOK: dict[str, str] = {
    "SQL_INJECTION": "playbook_sqli.md",
    "XSS": "playbook_xss.md",
    "BRUTE_FORCE": "playbook_bruteforce.md",

    # The current backend Classification enum does not yet expose
    # CSRF. This mapping is kept ready for future enum support.
    "CSRF": "playbook_csrf.md",
}


def get_playbook(classification: Any) -> str | None:
    """
    Return the playbook content for a classification.

    The function accepts either:
    - a string such as "SQL_INJECTION";
    - an Enum-like object exposing a .value attribute.

    Returns:
        The Markdown playbook content, or None when no playbook exists.
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
