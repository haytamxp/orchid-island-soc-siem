"""
Generate controlled stress-test variants of a labeled dataset.

Labels are preserved. Only observable fields are modified.
"""

from __future__ import annotations

import csv
import random
from pathlib import Path


SEED = 20260902
random.seed(SEED)


FIELDS = [
    "timestamp",
    "severity",
    "source",
    "category",
    "description",
    "src_ip",
    "dst_ip",
    "dst_port",
    "username",
    "hostname",
    "url",
    "http_method",
    "http_status",
    "bytes_in",
    "bytes_out",
    "action",
    "event_id",
    "label",
]


GENERIC_DESCRIPTIONS = [
    "Security event observed",
    "Application event",
    "Network activity observed",
    "Request processed",
    "Endpoint activity",
    "Authentication event",
]


def read_rows(
    path: Path,
) -> list[dict[str, str]]:
    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        return list(
            csv.DictReader(handle)
        )


def write_rows(
    path: Path,
    rows: list[dict[str, str]],
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=FIELDS,
        )

        writer.writeheader()
        writer.writerows(rows)


def anonymize_semantics(
    rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    result = []

    for row in rows:
        copy = dict(row)

        copy["description"] = random.choice(
            GENERIC_DESCRIPTIONS
        )

        copy["category"] = "generic"

        result.append(copy)

    return result


def shift_severity(
    rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    downgrade = {
        "critical": "high",
        "high": "medium",
        "medium": "low",
        "low": "low",
    }

    result = []

    for row in rows:
        copy = dict(row)
        copy["severity"] = downgrade.get(
            copy.get("severity", "").lower(),
            "low",
        )
        result.append(copy)

    return result


def shift_sources(
    rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    source_map = {
        "web": "cloudflare",
        "cloudflare": "web",
        "wazuh": "suricata",
        "suricata": "wazuh",
    }

    result = []

    for row in rows:
        copy = dict(row)

        copy["source"] = source_map.get(
            copy.get("source", "").lower(),
            copy.get("source", "web"),
        )

        result.append(copy)

    return result


def combined_shift(
    rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    result = shift_sources(
        shift_severity(
            anonymize_semantics(rows)
        )
    )

    return result


def generate(
    input_path: str,
    output_dir: str,
) -> dict[str, str]:
    source = Path(input_path)
    destination = Path(output_dir)

    rows = read_rows(source)

    outputs = {
        "baseline": (
            destination
            / "baseline.csv"
        ),
        "semantic_blind": (
            destination
            / "semantic_blind.csv"
        ),
        "severity_shift": (
            destination
            / "severity_shift.csv"
        ),
        "source_shift": (
            destination
            / "source_shift.csv"
        ),
        "combined_shift": (
            destination
            / "combined_shift.csv"
        ),
    }

    write_rows(
        outputs["baseline"],
        rows,
    )

    write_rows(
        outputs["semantic_blind"],
        anonymize_semantics(rows),
    )

    write_rows(
        outputs["severity_shift"],
        shift_severity(rows),
    )

    write_rows(
        outputs["source_shift"],
        shift_sources(rows),
    )

    write_rows(
        outputs["combined_shift"],
        combined_shift(rows),
    )

    return {
        name: str(path)
        for name, path in outputs.items()
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "Create behavioral ML stress datasets"
        )
    )

    parser.add_argument(
        "--input",
        required=True,
    )

    parser.add_argument(
        "--output-dir",
        default=(
            "database/"
            "ml_stress"
        ),
    )

    args = parser.parse_args()

    outputs = generate(
        args.input,
        args.output_dir,
    )

    for name, path in outputs.items():
        print(
            f"{name}: {path}"
        )
