"""Isolation Forest inference — loads once at startup, scores fused vectors."""

import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

_model: IsolationForest | None = None
_FEATURE_COLS = [
    "prior_cyber_alert_count",
    "max_cyber_severity",
    "transaction_count_3min",
    "transfer_velocity_3min",
    "ip_reputation_score",
    "time_delta_cyber_to_tx",
    "tls_risk_score",
    "mitre_tag",
    "fatf_tag",
]


def load_model(path: str | Path = "models/isolation_forest.pkl") -> None:
    global _model
    with open(path, "rb") as f:
        _model = pickle.load(f)


def score(fused_vector: dict) -> float:
    """
    Returns an anomaly score in [0, 1].
    Higher = more anomalous. Threshold ≥0.75 triggers an alert.
    """
    if _model is None:
        raise RuntimeError("Model not loaded — call load_model() first")

    row = {col: fused_vector.get(col, 0) for col in _FEATURE_COLS}
    df = pd.DataFrame([row])

    # IsolationForest.score_samples returns negative values — more negative = more anomalous
    raw = _model.score_samples(df)[0]

    # Normalise to [0, 1] where 1 is most anomalous
    # Typical range is roughly [-0.6, 0.0] for IF
    normalised = float(np.clip((raw + 0.6) / 0.6 * -1 + 1, 0.0, 1.0))
    return round(normalised, 4)
