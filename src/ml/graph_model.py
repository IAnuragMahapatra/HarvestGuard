"""GNN fraud ring detection. Embedding lookup on pre-trained GraphSAGE output."""

import pickle
from pathlib import Path

_embeddings: dict | None = None


def load_embeddings(path: str | Path = "models/graph_embeddings.pkl") -> None:
    global _embeddings
    with open(path, "rb") as f:
        _embeddings = pickle.load(f)


def ring_lookup(account_id: str) -> dict:
    """
    Returns fraud ring metadata for the given account.

    Response shape:
        {is_fraud_ring: bool, ring_members: list[str], cluster_id: int}
    """
    if _embeddings is None:
        return {"is_fraud_ring": False, "ring_members": [], "cluster_id": -1}

    entry = _embeddings.get(account_id, {})
    return {
        "is_fraud_ring": entry.get("is_fraud_ring", False),
        "ring_members": entry.get("ring_members", []),
        "cluster_id": entry.get("cluster_id", -1),
    }


def graph_nodes_for_alert(account_ids: list[str], src_ip: str) -> dict:
    """
    Builds echarts graph node/edge data for the Alert Detail graph view.

    Returns {"nodes": [...], "edges": [...]} compatible with streamlit-echarts.
    """
    if _embeddings is None:
        return {"nodes": [], "edges": []}

    seen_accounts = set()
    nodes = []
    edges = []

    # IP node
    ip_node_id = f"ip:{src_ip}"
    nodes.append({
        "id": ip_node_id,
        "name": src_ip,
        "category": 0,  # IP node, Electric Blue
        "symbolSize": 30,
        "label": {"show": True},
    })

    for acc in account_ids:
        if acc in seen_accounts:
            continue
        seen_accounts.add(acc)

        entry = _embeddings.get(acc, {})
        is_ring = entry.get("is_fraud_ring", False)

        node = {
            "id": acc,
            "name": acc,
            "category": 2 if is_ring else 1,  # 2=flagged(red), 1=normal(green)
            "symbolSize": 25 if is_ring else 18,
            "label": {"show": True},
        }
        nodes.append(node)
        edges.append({"source": ip_node_id, "target": acc, "lineStyle": {"type": "solid"}})

        # Add ring members as dimmer nodes
        for member in entry.get("ring_members", [])[:10]:
            if member not in seen_accounts and member != acc:
                seen_accounts.add(member)
                nodes.append({
                    "id": member,
                    "name": member,
                    "category": 3,  # amber / ring member
                    "symbolSize": 14,
                    "label": {"show": False},
                })
                edges.append({
                    "source": acc,
                    "target": member,
                    "lineStyle": {"type": "dashed"},
                })

    return {"nodes": nodes, "edges": edges}
