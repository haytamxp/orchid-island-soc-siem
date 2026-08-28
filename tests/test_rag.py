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


def test_csrf_playbook() -> None:
    playbook = get_playbook("CSRF")

    assert playbook is not None
    assert "Cross-Site Request Forgery" in playbook


def test_path_traversal_playbook() -> None:
    playbook = get_playbook("PATH_TRAVERSAL")

    assert playbook is not None
    assert "Path Traversal" in playbook


def test_malware_playbook() -> None:
    playbook = get_playbook("MALWARE")

    assert playbook is not None
    assert "Malware" in playbook


def test_credential_attack_playbook() -> None:
    playbook = get_playbook("CREDENTIAL_ATTACK")

    assert playbook is not None
    assert "Credential Attack" in playbook


def test_scanning_playbook() -> None:
    playbook = get_playbook("SCANNING")

    assert playbook is not None
    assert "Scanning" in playbook


def test_unknown_classification_returns_none() -> None:
    playbook = get_playbook("UNKNOWN")

    assert playbook is None