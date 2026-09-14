"""
UNSW-NB15 XGBoost benchmark for Orchid.

The benchmark consumes every row of the prepared UNSW corpus.
The split is temporal:
70% train / 15% validation / 15% test by stime.

attack_cat is intentionally absent from the model feature set.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.preprocessing import OneHotEncoder
from xgboost import XGBClassifier

from backend.ml.evaluation import (
    evaluate_binary,
    select_threshold,
)
from dataset_ingestion.unsw_features import (
    CATEGORICAL_COLUMNS,
    MODEL_COLUMNS,
    DERIVED_COLUMNS,
    NUMERIC_COLUMNS,
)


DEFAULT_MODEL = (
    "models/orchid_unsw_xgb.joblib"
)

DEFAULT_METRICS = (
    "models/orchid_unsw_metrics.json"
)


def positive_weight(
    labels: np.ndarray,
) -> float:
    negative = int(
        np.sum(labels == 0)
    )

    positive = int(
        np.sum(labels == 1)
    )

    if negative == 0 or positive == 0:
        raise ValueError(
            "Both classes are required"
        )

    return negative / positive


def build_sparse_matrix(
    frame: pd.DataFrame,
    encoder: OneHotEncoder,
    fit_encoder: bool,
) -> sparse.csr_matrix:
    numeric = frame[
        [
            *NUMERIC_COLUMNS,
            *DERIVED_COLUMNS,
        ]
    ].to_numpy(
        dtype=np.float32
    )

    numeric_matrix = sparse.csr_matrix(
        numeric
    )

    categorical = frame[
        CATEGORICAL_COLUMNS
    ].astype(str)

    if fit_encoder:
        categorical_matrix = (
            encoder.fit_transform(
                categorical
            )
        )
    else:
        categorical_matrix = (
            encoder.transform(
                categorical
            )
        )

    return sparse.hstack(
        [
            numeric_matrix,
            categorical_matrix,
        ],
        format="csr",
    )


def train(
    dataset_path: str,
    model_path: str = DEFAULT_MODEL,
    metrics_path: str = DEFAULT_METRICS,
) -> dict[str, Any]:
    dataset = Path(dataset_path)

    if not dataset.exists():
        raise FileNotFoundError(
            f"Prepared dataset not found: {dataset}"
        )

    frame = pd.read_csv(
        dataset
    )

    required = {
        *MODEL_COLUMNS,
        "label",
        "split",
    }

    missing = sorted(
        required.difference(frame.columns)
    )

    if missing:
        raise ValueError(
            "Prepared dataset is missing: "
            + ", ".join(missing)
        )

    if "attack_cat" in frame.columns:
        raise ValueError(
            "attack_cat must never reach the "
            "prepared ML dataset"
        )

    train_frame = frame[
        frame["split"] == "train"
    ].copy()

    validation_frame = frame[
        frame["split"] == "validation"
    ].copy()

    test_frame = frame[
        frame["split"] == "test"
    ].copy()

    y_train = train_frame[
        "label"
    ].to_numpy(dtype=np.int8)

    y_validation = validation_frame[
        "label"
    ].to_numpy(dtype=np.int8)

    y_test = test_frame[
        "label"
    ].to_numpy(dtype=np.int8)

    encoder = OneHotEncoder(
        handle_unknown="ignore",
        sparse_output=True,
        dtype=np.float32,
    )

    X_train = build_sparse_matrix(
        train_frame,
        encoder,
        fit_encoder=True,
    )

    X_validation = build_sparse_matrix(
        validation_frame,
        encoder,
        fit_encoder=False,
    )

    X_test = build_sparse_matrix(
        test_frame,
        encoder,
        fit_encoder=False,
    )

    weight = positive_weight(
        y_train
    )

    model = XGBClassifier(
        n_estimators=500,
        max_depth=7,
        learning_rate=0.05,
        min_child_weight=4,
        subsample=0.85,
        colsample_bytree=0.85,
        reg_alpha=0.10,
        reg_lambda=3.0,
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

    model_file = Path(model_path)
    metrics_file = Path(metrics_path)

    model_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    metrics_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    feature_names = [
        *NUMERIC_COLUMNS,
        *DERIVED_COLUMNS,
        *encoder.get_feature_names_out(
            CATEGORICAL_COLUMNS
        ).tolist(),
    ]

    joblib.dump(
        {
            "model": model,
            "encoder": encoder,
            "feature_names": feature_names,
            "threshold": threshold,
            "version": "unsw-v1",
            "target": "label",
            "excluded_columns": [
                "attack_cat",
            ],
            "split_policy": (
                "temporal 70/15/15"
            ),
        },
        model_file,
    )

    metrics = {
        "version": "unsw-v1",
        "dataset": str(dataset),
        "rows": int(len(frame)),
        "features": len(feature_names),
        "split_sizes": {
            "train": int(len(train_frame)),
            "validation": int(
                len(validation_frame)
            ),
            "test": int(len(test_frame)),
        },
        "class_counts": {
            "benign": int(
                np.sum(frame["label"] == 0)
            ),
            "malicious": int(
                np.sum(frame["label"] == 1)
            ),
        },
        "scale_pos_weight": weight,
        "threshold": threshold,
        "excluded_from_features": [
            "attack_cat",
        ],
        "validation": (
            validation_result.to_dict()
        ),
        "test": (
            test_result.to_dict()
        ),
        "feature_names": feature_names,
    }

    metrics_file.write_text(
        json.dumps(
            metrics,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("=== Orchid UNSW Benchmark ===")
    print(
        f"Rows: {metrics['rows']}"
    )
    print(
        f"Features: {metrics['features']}"
    )
    print(
        f"Train: "
        f"{metrics['split_sizes']['train']}"
    )
    print(
        f"Validation: "
        f"{metrics['split_sizes']['validation']}"
    )
    print(
        f"Test: "
        f"{metrics['split_sizes']['test']}"
    )
    print(
        f"Threshold: {threshold:.4f}"
    )
    print(
        "Test PR-AUC: "
        f"{test_result.pr_auc:.4f}"
    )
    print(
        "Test Precision: "
        f"{test_result.precision:.4f}"
    )
    print(
        "Test Recall: "
        f"{test_result.recall:.4f}"
    )
    print(
        "Test F1: "
        f"{test_result.f1:.4f}"
    )
    print(
        "Test FPR: "
        f"{test_result.false_positive_rate:.4f}"
    )
    print(
        "Test FNR: "
        f"{test_result.false_negative_rate:.4f}"
    )

    return metrics


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--dataset",
        default=(
            "data/processed/unsw_nb15/"
            "unsw_ml_ready.csv"
        ),
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

    train(
        dataset_path=args.dataset,
        model_path=args.model,
        metrics_path=args.metrics,
    )


if __name__ == "__main__":
    main()
