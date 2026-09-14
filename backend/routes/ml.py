"""
ML risk-scoring API routes.
"""

from pathlib import Path
from typing import Any

from flask import Blueprint, jsonify, request

from backend.ml.risk_model import RiskScorer


ml_bp = Blueprint(
    "ml",
    __name__,
    url_prefix="/api/ml",
)


MODEL_PATH = (
    Path(__file__).resolve().parents[2]
    / "models"
    / "orchid_risk_xgb.joblib"
)


scorer = RiskScorer(
    MODEL_PATH
)


@ml_bp.route(
    "/health",
    methods=["GET"],
)
def ml_health():
    """
    Return ML engine availability.
    """

    return jsonify(
        {
            "status": "ok",
            "model_available": scorer.available,
            "model_path": str(MODEL_PATH),
        }
    )


@ml_bp.route(
    "/score",
    methods=["POST"],
)
def score_event():
    """
    Score one security event.

    The endpoint accepts a JSON object representing a normalized
    security event.
    """

    payload: Any = request.get_json(
        silent=True
    )

    if not isinstance(payload, dict):
        return jsonify(
            {
                "error": "JSON object required",
            }
        ), 400

    try:
        prediction = scorer.predict(
            payload
        )
    except Exception as exc:
        return jsonify(
            {
                "error": "ML scoring failed",
                "details": str(exc),
            }
        ), 500

    return jsonify(
        {
            "success": True,
            "prediction": prediction.to_dict(),
        }
    )