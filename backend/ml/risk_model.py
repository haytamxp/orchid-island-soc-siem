"""
XGBoost-based risk scoring for Orchid Island SOC/SIEM.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
from xgboost import XGBClassifier

from backend.ml.features import extract_features


@dataclass(frozen=True)
class RiskPrediction:
    risk_score: float
    probability: float
    label: str
    confidence: float
    model_available: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "risk_score": self.risk_score,
            "probability": self.probability,
            "label": self.label,
            "confidence": self.confidence,
            "model_available": self.model_available,
        }


class RiskScorer:
    def __init__(self, model_path: str | Path):
        self.model_path = Path(model_path)
        self.model: XGBClassifier | None = None
        self.load()

    def load(self) -> bool:
        if not self.model_path.exists():
            self.model = None
            return False

        self.model = joblib.load(self.model_path)
        return True

    @property
    def available(self) -> bool:
        return self.model is not None

    def predict(self, event: dict[str, Any]) -> RiskPrediction:
        features = extract_features(event)

        vector = np.asarray(
            [features.to_vector()],
            dtype=np.float32,
        )

        if self.model is None:
            return self._fallback_prediction(
                features.to_vector()
            )

        probabilities = self.model.predict_proba(vector)[0]

        probability = (
            float(probabilities[1])
            if len(probabilities) >= 2
            else float(probabilities[0])
        )

        probability = max(
            0.0,
            min(1.0, probability),
        )

        risk_score = round(
            probability * 100.0,
            2,
        )

        if risk_score >= 85:
            label = "CRITICAL"
        elif risk_score >= 65:
            label = "HIGH"
        elif risk_score >= 35:
            label = "MEDIUM"
        else:
            label = "LOW"

        confidence = round(
            abs(probability - 0.5) * 2,
            4,
        )

        return RiskPrediction(
            risk_score=risk_score,
            probability=round(probability, 6),
            label=label,
            confidence=confidence,
            model_available=True,
        )

    @staticmethod
    def _fallback_prediction(
        vector: list[float],
    ) -> RiskPrediction:
        severity = vector[0]
        attack_features = sum(vector[14:23])

        heuristic_probability = min(
            1.0,
            (severity * 0.45)
            + (min(attack_features, 4.0) * 0.10)
            + (vector[24] * 0.10),
        )

        risk_score = round(
            heuristic_probability * 100,
            2,
        )

        if risk_score >= 85:
            label = "CRITICAL"
        elif risk_score >= 65:
            label = "HIGH"
        elif risk_score >= 35:
            label = "MEDIUM"
        else:
            label = "LOW"

        return RiskPrediction(
            risk_score=risk_score,
            probability=round(
                heuristic_probability,
                6,
            ),
            label=label,
            confidence=0.20,
            model_available=False,
        )
