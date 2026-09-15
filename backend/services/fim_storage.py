"""
Persistence helpers for File Integrity Monitoring.

This module intentionally isolates SQL/database operations from the
hashing and comparison logic.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from backend.services.db import execute, query_all, query_one


def upsert_baseline(
    hostname: str,
    file_path: str,
    sha256: str,
    file_size: int,
    mode: Optional[str] = None,
    owner_name: Optional[str] = None,
) -> int:
    """
    Create or replace the trusted baseline for one file.
    """

    sql = """
        INSERT INTO fim_baselines (
            hostname,
            file_path,
            sha256,
            file_size,
            mode,
            owner_name,
            monitored
        )
        VALUES (%s, %s, %s, %s, %s, %s, TRUE)
        ON DUPLICATE KEY UPDATE
            sha256 = VALUES(sha256),
            file_size = VALUES(file_size),
            mode = VALUES(mode),
            owner_name = VALUES(owner_name),
            monitored = TRUE,
            updated_at = CURRENT_TIMESTAMP
    """

    return execute(
        sql,
        (
            hostname,
            file_path,
            sha256,
            file_size,
            mode,
            owner_name,
        ),
    )


def get_baseline(
    hostname: str,
    file_path: str,
) -> Optional[dict]:
    """
    Retrieve the trusted baseline for a file.
    """

    sql = """
        SELECT
            id,
            hostname,
            file_path,
            sha256,
            file_size,
            mode,
            owner_name,
            monitored,
            created_at,
            updated_at
        FROM fim_baselines
        WHERE hostname = %s
          AND file_path = %s
        LIMIT 1
    """

    return query_one(sql, (hostname, file_path))


def list_baselines(
    hostname: Optional[str] = None,
    monitored_only: bool = True,
) -> list[dict]:
    """
    List configured FIM baselines.
    """

    conditions = []
    params: list = []

    if hostname:
        conditions.append("hostname = %s")
        params.append(hostname)

    if monitored_only:
        conditions.append("monitored = TRUE")

    where = ""

    if conditions:
        where = "WHERE " + " AND ".join(conditions)

    sql = f"""
        SELECT
            id,
            hostname,
            file_path,
            sha256,
            file_size,
            mode,
            owner_name,
            monitored,
            created_at,
            updated_at
        FROM fim_baselines
        {where}
        ORDER BY hostname ASC, file_path ASC
    """

    return query_all(sql, tuple(params))


def disable_baseline(
    hostname: str,
    file_path: str,
) -> int:
    """
    Disable monitoring of a baseline without deleting historical data.
    """

    sql = """
        UPDATE fim_baselines
        SET monitored = FALSE,
            updated_at = CURRENT_TIMESTAMP
        WHERE hostname = %s
          AND file_path = %s
    """

    return execute(sql, (hostname, file_path))


def insert_fim_event(
    hostname: str,
    file_path: str,
    change_type: str,
    old_hash: Optional[str],
    new_hash: Optional[str],
    old_size: Optional[int],
    new_size: Optional[int],
    severity: str,
    actor: Optional[str] = None,
    process_name: Optional[str] = None,
    agent_id: Optional[str] = None,
    details: Optional[str] = None,
) -> int:
    """
    Persist a detected integrity event.
    """

    sql = """
        INSERT INTO fim_events (
            hostname,
            timestamp,
            file_path,
            change_type,
            old_hash,
            new_hash,
            old_size,
            new_size,
            severity,
            actor,
            process_name,
            agent_id,
            details
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
    """

    return execute(
        sql,
        (
            hostname,
            datetime.utcnow(),
            file_path,
            change_type,
            old_hash,
            new_hash,
            old_size,
            new_size,
            severity,
            actor,
            process_name,
            agent_id,
            details,
        ),
    )


def list_fim_events(
    hostname: Optional[str] = None,
    severity: Optional[str] = None,
    change_type: Optional[str] = None,
    limit: int = 200,
) -> list[dict]:
    """
    Return recent FIM events with safe parameterized filtering.
    """

    limit = max(1, min(limit, 1000))

    conditions = []
    params: list = []

    if hostname:
        conditions.append("hostname = %s")
        params.append(hostname)

    if severity:
        conditions.append("severity = %s")
        params.append(severity)

    if change_type:
        conditions.append("change_type = %s")
        params.append(change_type)

    where = ""

    if conditions:
        where = "WHERE " + " AND ".join(conditions)

    sql = f"""
        SELECT
            id,
            hostname,
            timestamp,
            file_path,
            change_type,
            old_hash,
            new_hash,
            old_size,
            new_size,
            severity,
            actor,
            process_name,
            agent_id,
            details
        FROM fim_events
        {where}
        ORDER BY timestamp DESC
        LIMIT {limit}
    """

    return query_all(sql, tuple(params))