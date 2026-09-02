"""
Evaluation utilities for binary security classification.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np

from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


@dataclass(slots=True)
class BinaryEvaluation:
    threshold: float
    accuracy: float
    precision: float
    recall: float
    f1: float
    roc_auc: float
    pr_auc: float
    true_negatives: int
    false_positives: int
    false_negatives: int
    true_positives: int
    false_positive_rate: float
    false_negative_rate: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _safe_auc(
    function,
    y_true: np.ndarray,
    scores: np.ndarray,
) -> float:
    try:
        return float(
            function(
                y_true,
                scores,
            )
        )
    except ValueError:
        return 0.0


def evaluate_binary(
    y_true: np.ndarray,
    scores: np.ndarray,
    threshold: float,
) -> BinaryEvaluation:
    y_true = np.asarray(
        y_true,
        dtype=np.int8,
    )

    scores = np.asarray(
        scores,
        dtype=np.float64,
    )

    predictions = (
        scores >= threshold
    ).astype(np.int8)

    tn, fp, fn, tp = confusion_matrix(
        y_true,
        predictions,
        labels=[0, 1],
    ).ravel()

    negative_total = tn + fp
    positive_total = tp + fn

    return BinaryEvaluation(
        threshold=float(threshold),
        accuracy=float(
            accuracy_score(
                y_true,
                predictions,
            )
        ),
        precision=float(
            precision_score(
                y_true,
                predictions,
                zero_division=0,
            )
        ),
        recall=float(
            recall_score(
                y_true,
                predictions,
                zero_division=0,
            )
        ),
        f1=float(
            f1_score(
                y_true,
                predictions,
                zero_division=0,
            )
        ),
        roc_auc=_safe_auc(
            roc_auc_score,
            y_true,
            scores,
        ),
        pr_auc=_safe_auc(
            average_precision_score,
            y_true,
            scores,
        ),
        true_negatives=int(tn),
        false_positives=int(fp),
        false_negatives=int(fn),
        true_positives=int(tp),
        false_positive_rate=float(
            fp / negative_total
            if negative_total
            else 0.0
        ),
        false_negative_rate=float(
            fn / positive_total
            if positive_total
            else 0.0
        ),
    )


def select_threshold(
    y_true: np.ndarray,
    scores: np.ndarray,
    minimum_precision: float = 0.70,
) -> float:
    candidates = np.unique(
        np.clip(
            np.asarray(
                scores,
                dtype=np.float64,
            ),
            0.0,
            1.0,
        )
    )

    if candidates.size == 0:
        return 0.5

    candidates = np.unique(
        np.concatenate(
            [
                candidates,
                np.array(
                    [
                        0.05,
                        0.10,
                        0.20,
                        0.30,
                        0.40,
                        0.50,
                        0.60,
                        0.70,
                        0.80,
                        0.90,
                    ],
                    dtype=np.float64,
                ),
            ]
        )
    )

    best_threshold = 0.5
    best_score = -1.0

    fallback_threshold = 0.5
    fallback_score = -1.0

    for threshold in candidates:
        prediction = (
            scores >= threshold
        ).astype(np.int8)

        precision = precision_score(
            y_true,
            prediction,
            zero_division=0,
        )

        f1 = f1_score(
            y_true,
            prediction,
            zero_division=0,
        )

        if f1 > fallback_score:
            fallback_score = f1
            fallback_threshold = float(
                threshold
            )

        if (
            precision >= minimum_precision
            and f1 > best_score
        ):
            best_score = f1
            best_threshold = float(
                threshold
            )

    if best_score < 0:
        return fallback_threshold

    return best_threshold
