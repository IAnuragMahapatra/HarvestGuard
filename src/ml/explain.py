"""
SHAP explainability — waterfall values and base64 PNG for each alert.

We use shap.TreeExplainer on the Isolation Forest. If shap is not installed
(Python 3.14 compat issues), falls back to a simple feature-weight heuristic.
"""

import base64
import io
import logging
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger("explain")

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

# Baseline weights used as fallback when SHAP TreeExplainer fails
_FALLBACK_WEIGHTS = {
    "prior_cyber_alert_count": 0.41,
    "transfer_velocity_3min": 0.31,
    "ip_reputation_score": 0.19,
    "max_cyber_severity": 0.12,
    "tls_risk_score": 0.08,
    "transaction_count_3min": 0.06,
    "time_delta_cyber_to_tx": -0.05,
    "mitre_tag": 0.03,
    "fatf_tag": 0.02,
}


def shap_values(fused_vector: dict, model=None) -> dict:
    """Returns {feature: shap_value} for the top features. Tries TreeExplainer first."""
    row = {col: fused_vector.get(col, 0) for col in _FEATURE_COLS}

    if model is not None:
        try:
            import shap as shap_lib
            explainer = shap_lib.TreeExplainer(model)
            df = pd.DataFrame([row])
            sv = explainer.shap_values(df)
            if sv is not None and len(sv) > 0:
                values = sv[0] if hasattr(sv[0], "__len__") else sv
                return {col: round(float(v), 4) for col, v in zip(_FEATURE_COLS, values)}
        except Exception as exc:
            logger.debug("TreeExplainer failed (%s), using fallback weights", exc)

    # Fallback: scale weights by feature deviation from normal
    normal_means = {
        "prior_cyber_alert_count": 1.0,
        "max_cyber_severity": 1.5,
        "transaction_count_3min": 2.0,
        "transfer_velocity_3min": 20000.0,
        "ip_reputation_score": 0.85,
        "time_delta_cyber_to_tx": 1800.0,
        "tls_risk_score": 0.0,
        "mitre_tag": 1059,
        "fatf_tag": 0,
    }
    result = {}
    for col in _FEATURE_COLS:
        val = row.get(col, 0)
        mean = normal_means.get(col, 1)
        deviation = abs(val - mean) / max(abs(mean), 1)
        result[col] = round(float(_FALLBACK_WEIGHTS.get(col, 0.01) * deviation), 4)

    return result


def waterfall_png(shap_dict: dict) -> Optional[str]:
    """
    Renders a horizontal waterfall bar chart from SHAP values.
    Returns base64-encoded PNG string.
    """
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        items = sorted(shap_dict.items(), key=lambda x: abs(x[1]), reverse=True)[:8]
        features = [k for k, _ in items]
        values = [v for _, v in items]
        colors = ["#E53935" if v > 0 else "#29B6F6" for v in values]

        fig, ax = plt.subplots(figsize=(7, 3.5))
        fig.patch.set_facecolor("#1E2430")
        ax.set_facecolor("#1E2430")

        bars = ax.barh(features[::-1], values[::-1], color=colors[::-1], height=0.6)
        ax.axvline(0, color="#8892A4", linewidth=0.8)
        ax.set_xlabel("SHAP contribution", color="#E8EDF3", fontsize=9)
        ax.tick_params(colors="#E8EDF3", labelsize=8)
        for spine in ax.spines.values():
            spine.set_edgecolor("#8892A4")
        ax.set_title("Feature contributions to anomaly score", color="#E8EDF3", fontsize=10)

        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", dpi=110, facecolor=fig.get_facecolor())
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode("utf-8")

    except Exception as exc:
        logger.warning("Could not render SHAP waterfall: %s", exc)
        return None
