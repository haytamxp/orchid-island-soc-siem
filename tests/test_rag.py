"""
Tests for the local SOC RAG playbook retriever.
"""

from ai.rag.retriever import get_playbook


def test_sql_injection_playbook() -> None:
    playbook = get_playbook("SQL_INJECTION")

    assert playbook is not None
    assert "Injection SQL" in playbook


def test_xss_playbook() -> None:
    playbook = get_playbook("XSS")

    assert playbook is not None
    assert "Cross-Site Scripting" in playbook


def test_brute_force_playbook() -> None:
    playbook = get_playbook("BRUTE_FORCE")

    assert playbook is not None
    assert "Force Brute" in playbook


def test_csrf_playbook_mapping() -> None:
    playbook = get_playbook("CSRF")

    assert playbook is not None
    assert "Cross-Site Request Forgery" in playbook


def test_unknown_classification_returns_none() -> None:
    playbook = get_playbook("UNKNOWN")

    assert playbook is None


if __name__ == "__main__":
    print("RAG tests loaded successfully.")
