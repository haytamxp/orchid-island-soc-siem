"""
FIM API.

All FIM telemetry is stored in the real MariaDB database.
No mock/in-memory FIM records are returned.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from backend.schemas.fim import (
    FIMBaselineRequest,
    FIMCheckRequest,
    FIMEventRequest,
)
from backend.services.fim import compare_snapshot, snapshot_file
from backend.services.fim_db import FIMDatabaseError
from backend.services.fim_storage import (
    get_baseline,
    insert_fim_event,
    list_baselines,
    list_fim_events,
    upsert_baseline,
)

fim_bp = Blueprint(
    "fim",
    __name__,
    url_prefix="/api/fim",
)


def _serialize(value: Any) -> Any:
    """Convert database values to JSON-compatible values."""

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    if isinstance(value, dict):
        return {
            key: _serialize(item)
            for key, item in value.items()
        }

    if isinstance(value, list):
        return [_serialize(item) for item in value]

    return value


def _validation_error(exc: ValidationError):
    return jsonify(
        {
            "error": "validation_error",
            "details": exc.errors(),
        }
    ), 400


@fim_bp.route("", methods=["GET"])
def get_fim():
    """Return real FIM events."""

    try:
        hostname = request.args.get("hostname") or None
        severity = request.args.get("severity") or None
        change_type = request.args.get("change_type") or None

        try:
            limit = int(
                request.args.get(
                    "limit",
                    "200",
                )
            )
        except ValueError:
            return jsonify(
                {
                    "error": "validation_error",
                    "message": "limit must be an integer",
                }
            ), 400

        events = list_fim_events(
            hostname=hostname,
            severity=severity,
            change_type=change_type,
            limit=limit,
        )

        return jsonify(_serialize(events)), 200

    except FIMDatabaseError as exc:
        return jsonify(
            {
                "error": "fim_database_unavailable",
                "message": str(exc),
            }
        ), 503


@fim_bp.route("/baselines", methods=["GET"])
def get_fim_baselines():
    """Return real baselines."""

    try:
        hostname = request.args.get("hostname") or None

        baselines = list_baselines(
            hostname=hostname,
            monitored_only=True,
        )

        return jsonify(
            _serialize(baselines)
        ), 200

    except FIMDatabaseError as exc:
        return jsonify(
            {
                "error": "fim_database_unavailable",
                "message": str(exc),
            }
        ), 503


@fim_bp.route("/baselines", methods=["POST"])
def create_fim_baseline():
    """
    Register a baseline supplied by a monitoring agent.

    The server stores the snapshot sent by the agent.
    It does NOT read the agent's path from the Flask host.
    """

    try:
        payload = FIMBaselineRequest.model_validate(
            request.get_json(silent=True) or {}
        )
    except ValidationError as exc:
        return _validation_error(exc)

    try:
        baseline_id = upsert_baseline(
            hostname=payload.hostname,
            file_path=payload.file_path,
            sha256=payload.sha256,
            file_size=payload.file_size,
            mode=payload.mode,
            owner_name=payload.owner_name,
        )

        baseline = get_baseline(
            payload.hostname,
            payload.file_path,
        )

        return jsonify(
            {
                "id": baseline_id,
                "status": "baseline_registered",
                "agent_id": payload.agent_id,
                "baseline": _serialize(baseline),
            }
        ), 201

    except FIMDatabaseError as exc:
        return jsonify(
            {
                "error": "fim_database_unavailable",
                "message": str(exc),
            }
        ), 503


@fim_bp.route("/events", methods=["POST"])
def create_fim_event():
    """Store one real event from an agent."""

    try:
        payload = FIMEventRequest.model_validate(
            request.get_json(silent=True) or {}
        )
    except ValidationError as exc:
        return _validation_error(exc)

    try:
        event_id = insert_fim_event(
            hostname=payload.hostname,
            file_path=payload.file_path,
            change_type=payload.change_type,
            old_hash=payload.old_hash,
            new_hash=payload.new_hash,
            old_size=payload.old_size,
            new_size=payload.new_size,
            severity=payload.severity,
            actor=payload.actor,
            process_name=payload.process_name,
            agent_id=payload.agent_id,
            details=payload.details,
        )

        return jsonify(
            {
                "id": event_id,
                "status": "stored",
            }
        ), 201

    except FIMDatabaseError as exc:
        return jsonify(
            {
                "error": "fim_database_unavailable",
                "message": str(exc),
            }
        ), 503


@fim_bp.route("/check", methods=["POST"])
def check_fim():
    """
    Compare a local Flask-host file against a trusted baseline.

    This endpoint is retained for server-local checks.
    Windows agents use their own local watcher instead.
    """

    try:
        payload = FIMCheckRequest.model_validate(
            request.get_json(silent=True) or {}
        )
    except ValidationError as exc:
        return _validation_error(exc)

    try:
        baseline = get_baseline(
            payload.hostname,
            payload.file_path,
        )

        if baseline is None:
            return jsonify(
                {
                    "error": "baseline_not_found",
                    "message": "No trusted baseline exists for this file.",
                }
            ), 404

        current = None

        try:
            current = snapshot_file(
                payload.file_path
            )
        except FileNotFoundError:
            current = None

        comparison = compare_snapshot(
            baseline_hash=baseline["sha256"],
            baseline_size=baseline["file_size"],
            current=current,
            path=payload.file_path,
        )

        return jsonify(
            {
                "hostname": payload.hostname,
                "file_path": payload.file_path,
                "comparison": {
                    "exists": comparison.exists,
                    "change_type": comparison.change_type,
                    "old_hash": comparison.old_hash,
                    "new_hash": comparison.new_hash,
                    "old_size": comparison.old_size,
                    "new_size": comparison.new_size,
                    "severity": comparison.severity,
                },
            }
        ), 200

    except FIMDatabaseError as exc:
        return jsonify(
            {
                "error": "fim_database_unavailable",
                "message": str(exc),
            }
        ), 503