"""
Tests for the UNSW-to-Orchid ML pipeline.
"""

from __future__ import annotations

import pandas as pd

from dataset_ingestion.corpus_split import (
    assign_temporal_split,
)
from dataset_ingestion.unsw_features import (
    build_feature_frame,
)


def sample_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "sport": 1234,
                "dsport": 80,
                "proto": "tcp",
                "state": "CON",
                "service": "http",
                "dur": 1.5,
                "sbytes": 1000,
                "dbytes": 500,
                "sttl": 64,
                "dttl": 62,
                "sloss": 0,
                "dloss": 0,
                "sload": 500.0,
                "dload": 250.0,
                "spkts": 10,
                "dpkts": 5,
                "swin": 64240,
                "dwin": 28960,
                "stcpb": 1,
                "dtcpb": 2,
                "smeansz": 100,
                "dmeansz": 100,
                "trans_depth": 0,
                "res_bdy_len": 0,
                "sjit": 0.1,
                "djit": 0.2,
                "sintpkt": 0.3,
                "dintpkt": 0.4,
                "tcprtt": 0.5,
                "synack": 0.2,
                "ackdat": 0.1,
                "is_sm_ips_ports": 0,
                "ct_state_ttl": 1,
                "ct_flw_http_mthd": 1,
                "is_ftp_login": 0,
                "ct_ftp_cmd": 0,
                "ct_srv_src": 2,
                "ct_srv_dst": 3,
                "ct_dst_ltm": 4,
                "ct_src_ltm": 5,
                "ct_src_dport_ltm": 6,
                "ct_dst_sport_ltm": 7,
                "ct_dst_src_ltm": 8,
                "stime": 1451606400,
                "attack_cat": "Exploits",
                "label": 1,
            }
        ]
    )


def test_attack_category_is_not_a_feature() -> None:
    result = build_feature_frame(
        sample_frame()
    )

    assert "attack_cat" not in result.columns
    assert "label" in result.columns


def test_expected_derived_features_exist() -> None:
    result = build_feature_frame(
        sample_frame()
    )

    for column in (
        "total_bytes",
        "total_packets",
        "byte_ratio",
        "packet_ratio",
        "ttl_delta",
        "hour_sin",
        "hour_cos",
    ):
        assert column in result.columns


def test_label_is_binary_target() -> None:
    result = build_feature_frame(
        sample_frame()
    )

    assert int(
        result["label"].iloc[0]
    ) == 1


def test_temporal_split_is_monotonic() -> None:
    timestamps = pd.Series(
        [
            100,
            200,
            300,
            400,
            500,
        ]
    )

    result = assign_temporal_split(
        timestamps,
        train_cut=300,
        validation_cut=400,
    )

    assert result.tolist() == [
        "train",
        "train",
        "train",
        "validation",
        "test",
    ]
