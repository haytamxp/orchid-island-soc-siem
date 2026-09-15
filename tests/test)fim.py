"""
FIM tests.

The tests exercise the integrity logic independently from MySQL wherever
possible, then validate the API contract through the Flask test client.
"""

from __future__ import annotations

import hashlib

from backend.services.fim import (
    compare_snapshot,
    sha256_file,
    snapshot_file,
)


def test_sha256_file(tmp_path):
    test_file = tmp_path / "critical.conf"
    test_file.write_text(
        "original configuration\n",
        encoding="utf-8",
    )

    expected = hashlib.sha256(
        b"original configuration\n"
    ).hexdigest()

    assert sha256_file(test_file) == expected


def test_snapshot_file(tmp_path):
    test_file = tmp_path / "critical.conf"
    test_file.write_text(
        "configuration\n",
        encoding="utf-8",
    )

    snapshot = snapshot_file(test_file)

    assert snapshot.path.endswith("critical.conf")
    assert len(snapshot.sha256) == 64
    assert snapshot.size > 0


def test_compare_modified_file(tmp_path):
    test_file = tmp_path / "critical.conf"

    test_file.write_text(
        "safe=true\n",
        encoding="utf-8",
    )

    first_snapshot = snapshot_file(test_file)

    test_file.write_text(
        "safe=false\n",
        encoding="utf-8",
    )

    second_snapshot = snapshot_file(test_file)

    result = compare_snapshot(
        baseline_hash=first_snapshot.sha256,
        baseline_size=first_snapshot.size,
        current=second_snapshot,
        path=str(test_file),
    )

    assert result.exists is True
    assert result.change_type == "modified"
    assert result.old_hash == first_snapshot.sha256
    assert result.new_hash == second_snapshot.sha256
    assert result.old_hash != result.new_hash


def test_compare_deleted_file(tmp_path):
    test_file = tmp_path / "important.conf"
    test_file.write_text(
        "important=true\n",
        encoding="utf-8",
    )

    baseline = snapshot_file(test_file)

    test_file.unlink()

    result = compare_snapshot(
        baseline_hash=baseline.sha256,
        baseline_size=baseline.size,
        current=None,
        path=str(test_file),
    )

    assert result.exists is False
    assert result.change_type == "deleted"
    assert result.old_hash == baseline.sha256
    assert result.new_hash is None


def test_compare_unchanged_file(tmp_path):
    test_file = tmp_path / "unchanged.conf"
    test_file.write_text(
        "same=true\n",
        encoding="utf-8",
    )

    baseline = snapshot_file(test_file)

    result = compare_snapshot(
        baseline_hash=baseline.sha256,
        baseline_size=baseline.size,
        current=baseline,
        path=str(test_file),
    )

    assert result.exists is True
    assert result.change_type == "unchanged"


def test_get_fim(client):
    response = client.get("/api/fim")

    assert response.status_code == 200
    assert isinstance(response.get_json(), list)