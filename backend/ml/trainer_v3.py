"""
Behavior-first V3 XGBoost trainer.
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
from backend.ml.feature_pipeline_v3 import (
    build_dataset_from_csv,
)
from backend.ml.temporal_split import (
    temporal_split,
)


DEFAULT_MODEL = (
    "models/"
    "orchid_risk_xgb_v3.joblib"
)

DEFAULT_METRICS = (
    "models/"
    "orchid_risk_metrics_v3.json"
)


def positive_weight(
    labels: np.ndarray,
) -> float:
    negatives = int(
        np.sum(labels == 0)
    )

    positives = int(
        np.sum(labels == 1)
    )

    if negatives == 0 or positives == 0:
        raise ValueError(
            "Both classes are required"
        )

    return (
        negatives
        / positives
    )


def train(
    dataset_path: str,
    model_path: str = DEFAULT_MODEL,
    metrics_path: str = DEFAULT_METRICS,
) -> dict[str, Any]:

    dataset = build_dataset_from_csv(
        dataset_path
    )

    if len(dataset.labels) < 1000:
        raise ValueError(
            "V3 requires at least 1000 events"
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

    weight = positive_weight(
        y_train
    )

    model = XGBClassifier(
        n_estimators=600,
        max_depth=6,
        learning_rate=0.04,
        min_child_weight=4,
        subsample=0.85,
        colsample_bytree=0.85,
        reg_alpha=0.10,
        reg_lambda=2.5,
        objective="binary:logistic",
        eval_metric="aucpr",
        tree_method="hist",
        random_state=42,
        n_jobs=4,
        scale_pos_weight=weight,
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

    validation_result = (
        evaluate_binary(
            y_validation,
            validation_scores,
            threshold,
        )
    )

    test_result = (
        evaluate_binary(
            y_test,
            test_scores,
            threshold,
        )
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

    joblib.dump(
        {
            "model": model,
            "feature_names": (
                dataset.feature_names
            ),
            "threshold": threshold,
            "version": "v3",
            "feature_policy": (
                "behavior-first"
            ),
        },
        model_file,
    )

    metrics = {
        "version": "v3",
        "feature_policy": "behavior-first",
        "dataset": dataset_path,
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
        "scale_pos_weight": weight,
        "threshold": threshold,
        "validation": (
            validation_result.to_dict()
        ),
        "test": (
            test_result.to_dict()
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
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--dataset",
        required=True,
    )

    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
    )

    parser.add_argument(
        "--metrics",
        default=DEFAULT_METRICS,
    )

    args = parser.parse_args()

    metrics = train(
        dataset_path=args.dataset,
        model_path=args.model,
        metrics_path=args.metrics,
    )

    print(
        "V3 behavioral model trained."
    )

    print(
        f"Samples: "
        f"{metrics['samples']}"
    )

    print(
        f"Features: "
        f"{metrics['features']}"
    )

    print(
        f"Threshold: "
        f"{metrics['threshold']:.3f}"
    )

    print(
        f"Test PR-AUC: "
        f"{metrics['test']['pr_auc']:.4f}"
    )

    print(
        f"Test Precision: "
        f"{metrics['test']['precision']:.4f}"
    )

    print(
        f"Test Recall: "
        f"{metrics['test']['recall']:.4f}"
    )

    print(
        f"Test F1: "
        f"{metrics['test']['f1']:.4f}"
    )

    print(
        f"Test FPR: "
        f"{metrics['test']['false_positive_rate']:.4f}"
    )

    print(
        f"Test FNR: "
        f"{metrics['test']['false_negative_rate']:.4f}"
    )


if __name__ == "__main__":
    main()
