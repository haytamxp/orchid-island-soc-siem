"""
Behavioral XGBoost trainer.

Usage:

    python -m backend.ml.trainer_v2 --dataset database/ml_training_dataset.csv
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
from xgboost import XGBClassifier

from backend.ml.evaluation import (
    evaluate_binary,
    select_threshold,
)
from backend.ml.feature_pipeline import (
    build_dataset_from_csv,
)
from backend.ml.temporal_split import (
    temporal_split,
)


DEFAULT_MODEL_PATH = Path(
    "models/orchid_risk_xgb_v2.joblib"
)

DEFAULT_METRICS_PATH = Path(
    "models/orchid_risk_metrics_v2.json"
)


def _class_weight(
    y_train: np.ndarray,
) -> float:
    negatives = int(
        np.sum(y_train == 0)
    )

    positives = int(
        np.sum(y_train == 1)
    )

    if positives == 0:
        raise ValueError(
            "Training partition contains no malicious samples"
        )

    if negatives == 0:
        raise ValueError(
            "Training partition contains no benign samples"
        )

    return negatives / positives


def train(
    dataset_path: str | Path,
    model_path: str | Path = DEFAULT_MODEL_PATH,
    metrics_path: str | Path = DEFAULT_METRICS_PATH,
) -> dict[str, Any]:
    dataset = build_dataset_from_csv(
        dataset_path
    )

    split = temporal_split(
        dataset.timestamps,
        train_ratio=0.70,
        validation_ratio=0.15,
    )

    X_train = dataset.features[
        split.train_indices
    ]

    y_train = dataset.labels[
        split.train_indices
    ]

    X_validation = dataset.features[
        split.validation_indices
    ]

    y_validation = dataset.labels[
        split.validation_indices
    ]

    X_test = dataset.features[
        split.test_indices
    ]

    y_test = dataset.labels[
        split.test_indices
    ]

    scale_pos_weight = _class_weight(
        y_train
    )

    model = XGBClassifier(
        n_estimators=500,
        max_depth=6,
        learning_rate=0.05,
        min_child_weight=3,
        subsample=0.85,
        colsample_bytree=0.85,
        reg_alpha=0.05,
        reg_lambda=2.0,
        objective="binary:logistic",
        eval_metric="aucpr",
        tree_method="hist",
        random_state=42,
        n_jobs=4,
        scale_pos_weight=scale_pos_weight,
    )

    model.fit(
        X_train,
        y_train,
        eval_set=[
            (
                X_validation,
                y_validation,
            )
        ],
        verbose=False,
    )

    validation_scores = (
        model.predict_proba(
            X_validation
        )[:, 1]
    )

    threshold = select_threshold(
        y_validation,
        validation_scores,
        minimum_precision=0.70,
    )

    test_scores = (
        model.predict_proba(
            X_test
        )[:, 1]
    )

    validation_metrics = evaluate_binary(
        y_validation,
        validation_scores,
        threshold,
    )

    test_metrics = evaluate_binary(
        y_test,
        test_scores,
        threshold,
    )

    model_file = Path(
        model_path
    )

    metrics_file = Path(
        metrics_path
    )

    model_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    metrics_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    artifact = {
        "model": model,
        "feature_names": dataset.feature_names,
        "threshold": threshold,
        "version": "v2",
    }

    joblib.dump(
        artifact,
        model_file,
    )

    metrics = {
        "dataset": str(
            dataset_path
        ),
        "version": "v2",
        "samples": int(
            len(dataset.labels)
        ),
        "features": int(
            dataset.features.shape[1]
        ),
        "class_counts": {
            "benign": int(
                np.sum(
                    dataset.labels == 0
                )
            ),
            "malicious": int(
                np.sum(
                    dataset.labels == 1
                )
            ),
        },
        "split_sizes": {
            "train": int(
                len(y_train)
            ),
            "validation": int(
                len(y_validation)
            ),
            "test": int(
                len(y_test)
            ),
        },
        "scale_pos_weight": scale_pos_weight,
        "decision_threshold": threshold,
        "validation": (
            validation_metrics.to_dict()
        ),
        "test": (
            test_metrics.to_dict()
        ),
        "feature_names": (
            dataset.feature_names
        ),
    }

    metrics_file.write_text(
        json.dumps(
            metrics,
            indent=2,
        ),
        encoding="utf-8",
    )

    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Train Orchid Island "
            "behavioral risk model"
        )
    )

    parser.add_argument(
        "--dataset",
        required=True,
    )

    parser.add_argument(
        "--model",
        default=str(
            DEFAULT_MODEL_PATH
        ),
    )

    parser.add_argument(
        "--metrics",
        default=str(
            DEFAULT_METRICS_PATH
        ),
    )

    args = parser.parse_args()

    metrics = train(
        dataset_path=args.dataset,
        model_path=args.model,
        metrics_path=args.metrics,
    )

    validation = metrics[
        "validation"
    ]

    test = metrics["test"]

    print(
        "Behavioral model trained successfully."
    )

    print(
        f"Samples: {metrics['samples']}"
    )

    print(
        f"Features: {metrics['features']}"
    )

    print(
        f"Train: {metrics['split_sizes']['train']}"
    )

    print(
        f"Validation: "
        f"{metrics['split_sizes']['validation']}"
    )

    print(
        f"Test: {metrics['split_sizes']['test']}"
    )

    print(
        f"Threshold: "
        f"{metrics['decision_threshold']:.3f}"
    )

    print(
        f"Validation F1: "
        f"{validation['f1']:.4f}"
    )

    print(
        f"Validation PR-AUC: "
        f"{validation['pr_auc']:.4f}"
    )

    print(
        f"Test F1: "
        f"{test['f1']:.4f}"
    )

    print(
        f"Test PR-AUC: "
        f"{test['pr_auc']:.4f}"
    )

    print(
        f"Test Precision: "
        f"{test['precision']:.4f}"
    )

    print(
        f"Test Recall: "
        f"{test['recall']:.4f}"
    )

    print(
        f"Test FPR: "
        f"{test['false_positive_rate']:.4f}"
    )

    print(
        f"Test FNR: "
        f"{test['false_negative_rate']:.4f}"
    )


if __name__ == "__main__":
    main()
