"""
Command-line prediction utility for Orchid ML risk scoring.

The utility accepts JSON either:
1. As a single command-line argument.
2. From stdin, which is preferred on Windows PowerShell.
"""

import json
import sys
from pathlib import Path

from backend.ml.risk_model import RiskScorer


MODEL_PATH = (
    Path(__file__).resolve().parents[2]
    / "models"
    / "orchid_risk_xgb.joblib"
)


def load_event() -> dict:
    """
    Load a JSON event from stdin or argv.

    Stdin is preferred because PowerShell 5.1 can alter quoting
    when JSON is passed to a native executable.
    """

    if not sys.stdin.isatty():
        raw = sys.stdin.read().strip()

        if raw:
            try:
                event = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON from stdin: {exc}"
                ) from exc

            if not isinstance(event, dict):
                raise ValueError(
                    "Input JSON must be an object."
                )

            return event

    if len(sys.argv) != 2:
        raise ValueError(
            "Provide a JSON event as an argument or through stdin."
        )

    try:
        event = json.loads(sys.argv[1])
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Invalid JSON argument: {exc}"
        ) from exc

    if not isinstance(event, dict):
        raise ValueError(
            "Input JSON must be an object."
        )

    return event


def main() -> None:
    try:
        event = load_event()

        scorer = RiskScorer(
            MODEL_PATH
        )

        result = scorer.predict(
            event
        )

        print(
            json.dumps(
                result.to_dict(),
                indent=2,
            )
        )

    except ValueError as exc:
        print(
            f"Input error: {exc}"
        )
        raise SystemExit(1)

    except Exception as exc:
        print(
            f"Prediction error: {exc}"
        )
        raise SystemExit(1)


if __name__ == "__main__":
    main()
