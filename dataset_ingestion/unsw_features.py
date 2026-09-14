"""
Leakage-safe UNSW-NB15 feature engineering for Orchid.

Design:
- label is the binary target.
- attack_cat is evaluation metadata and NEVER a model feature.
- source/destination IPs are excluded from ML features.
- raw absolute timestamps are excluded from ML features.
- temporal context is represented only through hour-of-day cyclic features.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


CATEGORICAL_COLUMNS = [
    "proto",
    "state",
    "service",
]


NUMERIC_COLUMNS = [
    "sport",
    "dsport",
    "dur",
    "sbytes",
    "dbytes",
    "sttl",
    "dttl",
    "sloss",
    "dloss",
    "sload",
    "dload",
    "spkts",
    "dpkts",
    "swin",
    "dwin",
    "stcpb",
    "dtcpb",
    "smeansz",
    "dmeansz",
    "trans_depth",
    "res_bdy_len",
    "sjit",
    "djit",
    "sintpkt",
    "dintpkt",
    "tcprtt",
    "synack",
    "ackdat",
    "is_sm_ips_ports",
    "ct_state_ttl",
    "ct_flw_http_mthd",
    "is_ftp_login",
    "ct_ftp_cmd",
    "ct_srv_src",
    "ct_srv_dst",
    "ct_dst_ltm",
    "ct_src_ltm",
    "ct_src_dport_ltm",
    "ct_dst_sport_ltm",
    "ct_dst_src_ltm",
]


DERIVED_COLUMNS = [
    "total_bytes",
    "total_packets",
    "byte_ratio",
    "packet_ratio",
    "load_ratio",
    "ttl_delta",
    "loss_total",
    "bytes_per_packet",
    "src_bytes_per_packet",
    "dst_bytes_per_packet",
    "handshake_ratio",
    "ack_ratio",
    "connection_density",
    "service_src_density",
    "service_dst_density",
    "hour_sin",
    "hour_cos",
]


MODEL_COLUMNS = [
    *NUMERIC_COLUMNS,
    *DERIVED_COLUMNS,
    *CATEGORICAL_COLUMNS,
]


def _numeric(
    frame: pd.DataFrame,
    column: str,
) -> pd.Series:
    return pd.to_numeric(
        frame[column],
        errors="coerce",
    ).fillna(0.0)


def build_feature_frame(
    frame: pd.DataFrame,
) -> pd.DataFrame:
    required = {
        *NUMERIC_COLUMNS,
        *CATEGORICAL_COLUMNS,
        "stime",
        "label",
    }

    missing = sorted(
        required.difference(frame.columns)
    )

    if missing:
        raise ValueError(
            "Missing UNSW columns: "
            + ", ".join(missing)
        )

    result = pd.DataFrame(
        index=frame.index
    )

    for column in NUMERIC_COLUMNS:
        result[column] = _numeric(
            frame,
            column,
        ).astype(np.float32)

    sbytes = result["sbytes"].clip(
        lower=0
    )

    dbytes = result["dbytes"].clip(
        lower=0
    )

    spkts = result["spkts"].clip(
        lower=0
    )

    dpkts = result["dpkts"].clip(
        lower=0
    )

    result["total_bytes"] = (
        np.log1p(
            sbytes + dbytes
        ).astype(np.float32)
    )

    result["total_packets"] = (
        np.log1p(
            spkts + dpkts
        ).astype(np.float32)
    )

    result["byte_ratio"] = (
        (sbytes + 1.0)
        / (dbytes + 1.0)
    ).astype(np.float32)

    result["packet_ratio"] = (
        (spkts + 1.0)
        / (dpkts + 1.0)
    ).astype(np.float32)

    result["load_ratio"] = (
        (result["sload"] + 1.0)
        / (result["dload"] + 1.0)
    ).astype(np.float32)

    result["ttl_delta"] = (
        result["sttl"] - result["dttl"]
    ).astype(np.float32)

    result["loss_total"] = (
        result["sloss"] + result["dloss"]
    ).astype(np.float32)

    result["bytes_per_packet"] = (
        (sbytes + dbytes + 1.0)
        / (spkts + dpkts + 1.0)
    ).astype(np.float32)

    result["src_bytes_per_packet"] = (
        (sbytes + 1.0)
        / (spkts + 1.0)
    ).astype(np.float32)

    result["dst_bytes_per_packet"] = (
        (dbytes + 1.0)
        / (dpkts + 1.0)
    ).astype(np.float32)

    result["handshake_ratio"] = (
        (result["synack"] + 1.0)
        / (result["tcprtt"] + 1.0)
    ).astype(np.float32)

    result["ack_ratio"] = (
        (result["ackdat"] + 1.0)
        / (result["tcprtt"] + 1.0)
    ).astype(np.float32)

    result["connection_density"] = (
        np.log1p(
            result["ct_dst_src_ltm"]
        )
    ).astype(np.float32)

    result["service_src_density"] = (
        np.log1p(
            result["ct_srv_src"]
        )
    ).astype(np.float32)

    result["service_dst_density"] = (
        np.log1p(
            result["ct_srv_dst"]
        )
    ).astype(np.float32)

    timestamp = pd.to_datetime(
        pd.to_numeric(
            frame["stime"],
            errors="coerce",
        ),
        unit="s",
        utc=True,
        errors="coerce",
    )

    hour = (
        timestamp.dt.hour
        .fillna(0)
        .to_numpy(
            dtype=np.float32
        )
    )

    result["hour_sin"] = np.sin(
        2.0 * np.pi * hour / 24.0
    ).astype(np.float32)

    result["hour_cos"] = np.cos(
        2.0 * np.pi * hour / 24.0
    ).astype(np.float32)

    for column in CATEGORICAL_COLUMNS:
        result[column] = (
            frame[column]
            .fillna("UNKNOWN")
            .astype(str)
            .str.strip()
            .replace("", "UNKNOWN")
        )

    result["label"] = (
        pd.to_numeric(
            frame["label"],
            errors="coerce",
        )
        .fillna(0)
        .astype(np.int8)
    )

    return result[
        [
            *NUMERIC_COLUMNS,
            *DERIVED_COLUMNS,
            *CATEGORICAL_COLUMNS,
            "label",
        ]
    ]
