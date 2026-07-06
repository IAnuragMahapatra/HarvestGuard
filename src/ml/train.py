"""
Standalone training script. Run once after generate_baseline.py.

Reads the baseline JSON files, builds fused vectors, fits Isolation Forest,
and saves models/isolation_forest.pkl.

Not called at API runtime.
"""

import json
import pickle
from pathlib import Path

import pandas as pd
from sklearn.ensemble import IsolationForest

ROOT = Path(__file__).resolve().parents[2]
SAMPLE_DIR = ROOT / "sample_data"
MODELS_DIR = ROOT / "models"

FEATURE_COLS = [
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

MITRE_TAG_MAP = {
    "T1046": 1046, "T1059": 1059, "T1071": 1071,
    "T1078": 1078, "T1110": 1110, "T1133": 1133,
    "T1190": 1190, "T1566": 1566,
}


def load_data():
    tx_path = SAMPLE_DIR / "baseline_transactions.json"
    cy_path = SAMPLE_DIR / "baseline_telemetry.json"

    if not tx_path.exists() or not cy_path.exists():
        raise FileNotFoundError("Run generate_baseline.py first")

    transactions = json.loads(tx_path.read_text())
    cyber = json.loads(cy_path.read_text())
    return transactions, cyber


def pair_events(transactions, cyber, n_vectors=10_000):
    """Build synthetic fused vectors from baseline events."""
    import random
    rng = random.Random(42)

    vectors = []
    for _ in range(n_vectors):
        cy_sample = rng.sample(cyber, min(3, len(cyber)))
        tx_sample = rng.sample(transactions, min(2, len(transactions)))

        mitre_ints = [MITRE_TAG_MAP.get(e.get("mitre_tag", ""), 0) for e in cy_sample]
        fatf_ints = []
        for e in tx_sample:
            tag = e.get("fatf_tag")
            if tag:
                try:
                    fatf_ints.append(int(str(tag).split("-")[-1]))
                except (ValueError, IndexError):
                    pass

        vectors.append({
            "prior_cyber_alert_count": len(cy_sample),
            "max_cyber_severity": max((e.get("severity", 0) for e in cy_sample), default=0),
            "transaction_count_3min": rng.randint(1, 3),
            "transfer_velocity_3min": sum(e.get("amount_inr", 0) for e in tx_sample),
            "ip_reputation_score": rng.uniform(0.7, 1.0),
            "time_delta_cyber_to_tx": rng.uniform(60, 3600),
            "tls_risk_score": 0.0,
            "mitre_tag": max(mitre_ints) if mitre_ints else 0,
            "fatf_tag": max(fatf_ints) if fatf_ints else 0,
        })

    return vectors


def main():
    MODELS_DIR.mkdir(exist_ok=True)
    print("Loading baseline data...")
    transactions, cyber = load_data()
    print(f"  {len(transactions)} transactions, {len(cyber)} cyber events")

    print("Building fused vectors...")
    vectors = pair_events(transactions, cyber)
    df = pd.DataFrame(vectors)[FEATURE_COLS]

    print(f"Training Isolation Forest on {len(df)} vectors...")
    model = IsolationForest(n_estimators=200, contamination=0.05, random_state=42, n_jobs=-1)
    model.fit(df)

    out_path = MODELS_DIR / "isolation_forest.pkl"
    with open(out_path, "wb") as f:
        pickle.dump(model, f)
    print(f"  Model saved → {out_path}")


if __name__ == "__main__":
    main()
