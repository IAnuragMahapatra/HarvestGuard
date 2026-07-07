"""
Generates synthetic baseline data and trains the Isolation Forest.

Run once before starting the API:
    uv run python src/scripts/generate_baseline.py
"""

import json
import pickle
import random
from pathlib import Path

import numpy as np
import pandas as pd
from faker import Faker
from sklearn.ensemble import IsolationForest

fake = Faker("en_IN")
rng = random.Random(42)
np_rng = np.random.default_rng(42)

ROOT = Path(__file__).resolve().parents[2]
SAMPLE_DIR = ROOT / "sample_data"
MODELS_DIR = ROOT / "models"

MITRE_TAGS = [1001, 1046, 1059, 1071, 1078, 1110, 1133, 1190, 1566]
FATF_TAGS = [0, 1, 2, 3, 4, 5, 6, 7, 8]  # 0 = none
IP_POOL = [fake.ipv4_private() for _ in range(300)]
ACCOUNT_POOL = [f"ACC-{i:04d}" for i in range(500)]

N_TRANSACTIONS = 200
N_CYBER = 500
N_FUSED = 10_000


def _fused_vector(
    prior_cyber_alert_count: int,
    max_cyber_severity: float,
    transaction_count_3min: int,
    transfer_velocity_3min: float,
    ip_reputation_score: float,
    time_delta_cyber_to_tx: float,
    tls_risk_score: float,
    mitre_tag: int,
    fatf_tag: int,
) -> dict:
    return {
        "prior_cyber_alert_count": prior_cyber_alert_count,
        "max_cyber_severity": max_cyber_severity,
        "transaction_count_3min": transaction_count_3min,
        "transfer_velocity_3min": transfer_velocity_3min,
        "ip_reputation_score": ip_reputation_score,
        "time_delta_cyber_to_tx": time_delta_cyber_to_tx,
        "tls_risk_score": tls_risk_score,
        "mitre_tag": mitre_tag,
        "fatf_tag": fatf_tag,
    }


def generate_normal_transaction() -> dict:
    ts = fake.date_time_between(start_date="-30d", end_date="now").isoformat()
    src_ip = rng.choice(IP_POOL)
    return {
        "event_id": fake.uuid4(),
        "timestamp": ts,
        "src_ip": src_ip,
        "account_id": rng.choice(ACCOUNT_POOL),
        "dest_account_id": rng.choice(ACCOUNT_POOL),
        "amount_inr": round(rng.uniform(500, 45_000), 2),
        "fatf_tag": None,
        "branch_id": f"BR-{rng.randint(1, 50):03d}",
        "type": "transaction",
    }


def generate_normal_cyber() -> dict:
    ts = fake.date_time_between(start_date="-30d", end_date="now").isoformat()
    return {
        "event_id": fake.uuid4(),
        "timestamp": ts,
        "src_ip": rng.choice(IP_POOL),
        "dest_ip": fake.ipv4(),
        "mitre_tag": f"T{rng.choice([1046, 1059, 1071, 1133])}",
        "severity": round(rng.uniform(0.5, 3.5), 2),
        "tls_metadata": None,
        "type": "cyber",
    }


def generate_normal_fused_vectors(n: int) -> list[dict]:
    vectors = []
    for _ in range(n):
        v = _fused_vector(
            prior_cyber_alert_count=rng.randint(0, 2),
            max_cyber_severity=round(rng.uniform(0.0, 3.0), 2),
            transaction_count_3min=rng.randint(1, 3),
            transfer_velocity_3min=round(rng.uniform(500, 40_000), 2),
            ip_reputation_score=round(rng.uniform(0.7, 1.0), 3),
            time_delta_cyber_to_tx=round(rng.uniform(60, 3600), 1),
            tls_risk_score=0.0,
            mitre_tag=rng.choice([1046, 1059, 1071, 1133]),
            fatf_tag=0,
        )
        vectors.append(v)
    return vectors


def train_isolation_forest(vectors: list[dict]) -> IsolationForest:
    df = pd.DataFrame(vectors)
    model = IsolationForest(
        n_estimators=200,
        contamination=0.05,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(df)
    return model


def generate_graph_embeddings() -> dict:
    """
    Synthetic fraud ring graph.

    Five rings of ~20 mule accounts each embedded in 500 normal accounts.
    Returns a dict keyed by account_id with embedding vector + ring metadata.
    """
    all_accounts = ACCOUNT_POOL.copy()
    ring_clusters = {}
    is_fraud_ring = {}
    ring_members_map = {}

    for ring_id in range(1, 6):
        members = rng.sample(all_accounts, 20)
        for acc in members:
            is_fraud_ring[acc] = True
            ring_clusters[acc] = ring_id
            ring_members_map[acc] = members

    # Fake 64-dim embeddings: fraud ring accounts cluster away from normal
    embeddings = {}
    for acc in all_accounts:
        if is_fraud_ring.get(acc):
            cluster_id = ring_clusters[acc]
            center = np_rng.standard_normal(64) * 0.3 + cluster_id
        else:
            center = np_rng.standard_normal(64) * 0.5
        embeddings[acc] = {
            "embedding": center.tolist(),
            "is_fraud_ring": is_fraud_ring.get(acc, False),
            "cluster_id": ring_clusters.get(acc, -1),
            "ring_members": ring_members_map.get(acc, []),
        }

    # Ensure demo accounts are in a ring (Op 1 & Op 2)
    demo_accounts = ["ACC-0042", "ACC-0071", "ACC-0088", "ACC-0103", "ACC-0999"]
    demo_ring_members = demo_accounts + rng.sample(all_accounts, 16)
    for acc in demo_accounts:
        embeddings[acc] = {
            "embedding": (np_rng.standard_normal(64) * 0.3 + 99).tolist(),
            "is_fraud_ring": True,
            "cluster_id": 99,
            "ring_members": demo_ring_members,
        }

    # Op 3 Insider accounts
    insider_accounts = ["ACC-8888", "ACC-9999-OFFSHORE"]
    insider_ring_members = insider_accounts + rng.sample(all_accounts, 5)
    for acc in insider_accounts:
        embeddings[acc] = {
            "embedding": (np_rng.standard_normal(64) * 0.3 + 100).tolist(),
            "is_fraud_ring": True,
            "cluster_id": 100,
            "ring_members": insider_ring_members,
        }

    return embeddings


def main():
    SAMPLE_DIR.mkdir(exist_ok=True)
    MODELS_DIR.mkdir(exist_ok=True)

    print("Generating baseline transactions...")
    transactions = [generate_normal_transaction() for _ in range(N_TRANSACTIONS)]
    (SAMPLE_DIR / "baseline_transactions.json").write_text(
        json.dumps(transactions, indent=2)
    )
    print(f"  {len(transactions)} transactions → sample_data/baseline_transactions.json")

    print("Generating baseline cyber telemetry...")
    cyber = [generate_normal_cyber() for _ in range(N_CYBER)]
    (SAMPLE_DIR / "baseline_telemetry.json").write_text(json.dumps(cyber, indent=2))
    print(f"  {len(cyber)} cyber events → sample_data/baseline_telemetry.json")

    print(f"Generating {N_FUSED} normal fused vectors for training...")
    vectors = generate_normal_fused_vectors(N_FUSED)

    print("Training Isolation Forest...")
    model = train_isolation_forest(vectors)
    with open(MODELS_DIR / "isolation_forest.pkl", "wb") as f:
        pickle.dump(model, f)
    print("  Model → models/isolation_forest.pkl")

    print("Generating GNN fraud ring embeddings...")
    embeddings = generate_graph_embeddings()
    with open(MODELS_DIR / "graph_embeddings.pkl", "wb") as f:
        pickle.dump(embeddings, f)
    print(f"  {len(embeddings)} account embeddings → models/graph_embeddings.pkl")

    print("\nBaseline generation complete. Ready for demo.")


if __name__ == "__main__":
    main()
