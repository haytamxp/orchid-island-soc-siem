"""
Train the Orchid Island XGBoost risk model.
"""

import csv
import sys
from pathlib import Path
from typing import Any

import joblib
import numpy as np
from xgboost import XGBClassifier

from backend.ml.features import extract_features


MODEL_DIR = (
    Path(__file__).resolve().parents[2]
    / "models"
)

MODEL_PATH = (
    MODEL_DIR
    / "orchid_risk_xgb.joblib"
)


def parse_value(value: str) -> Any:
    value = value.strip()
    return value if value else None


def load_dataset(
    csv_path: Path,
) -> tuple[np.ndarray, np.ndarray]:

    features: list[list[float]] = []
    labels: list[int] = []

    with csv_path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:

        reader = csv.DictReader(handle)

        if reader.fieldnames is None:
            raise ValueError(
                "Dataset does not contain CSV headers."
            )

        if "label" not in reader.fieldnames:
            raise ValueError(
                "Dataset must contain a 'label' column."
            )

        for row in reader:
            event = {
                key: parse_value(value or "")
                for key, value in row.items()
                if key != "label"
            }

            try:
                label = int(row["label"])
            except (TypeError, ValueError):
                raise ValueError(
                    f"Invalid label: {row['label']!r}"
                )

            if label not in {0, 1}:
                raise ValueError(
                    "Labels must be 0 or 1."
                )

            features.append(
                extract_features(event).to_vector()
            )

            labels.append(label)

    if not features:
        raise ValueError(
            "Dataset is empty."
        )

    return (
        np.asarray(
            features,
            dtype=np.float32,
        ),
        np.asarray(
            labels,
            dtype=np.int32,
        ),
    )


def train(csv_path: Path) -> None:
    X, y = load_dataset(csv_path)

    unique_labels = set(y.tolist())

    if unique_labels != {0, 1}:
        raise ValueError(
            "Training requires both benign (0) "
            "and malicious (1) events."
        )

    model = XGBClassifier(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        objective="binary:logistic",
        eval_metric="logloss",
        random_state=42,
        n_jobs=2,
    )

    model.fit(X, y)

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(
        model,
        MODEL_PATH,
    )

    print(
        "Model trained successfully."
    )
    print(
        f"Samples: {len(y)}"
    )
    print(
        f"Features: {X.shape[1]}"
    )
    print(
        f"Model: {MODEL_PATH}"
    )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(
            "Usage: python -m backend.ml.train "
            "path/to/dataset.csv"
        )
        raise SystemExit(1)

    train(
        Path(sys.argv[1]).resolve()
    )
