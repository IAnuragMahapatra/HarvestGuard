"""
Injects the "Operation Smurfing Phantom" demo scenario into the running API.

Usage:
    uv run python src/scripts/run_demo.py
    uv run python src/scripts/run_demo.py --fast      # no delays between events
    uv run python src/scripts/run_demo.py --base-url http://localhost:8000
"""

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[2]
SAMPLE_DIR = ROOT / "sample_data"

DEMO_EVENTS = [
    # ---------------------------------------------------------
    # OPERATION 1: SMURFING PHANTOM & OPERATION 3: INSIDER 
    # (Interleaved early stages)
    # ---------------------------------------------------------
    
    # T+0s: port scan (Op 1)
    {
        "offset_seconds": 0,
        "endpoint": "/ingest/cyber",
        "payload": {
            "event_id": "demo-cyber-001",
            "timestamp": None,
            "src_ip": "10.0.0.99",
            "dest_ip": "10.0.0.1",
            "mitre_tag": "T1046",
            "severity": 3.0,
            "tls_metadata": None,
        },
        "label": "T+0s   | [Op 1] Port scan from 10.0.0.99 [T1046]",
    },
    
    # T+5s: Insider login outside hours (Op 3)
    {
        "offset_seconds": 5,
        "endpoint": "/ingest/cyber",
        "payload": {
            "event_id": "demo-cyber-005",
            "timestamp": None,
            "src_ip": "10.0.0.12",
            "dest_ip": "10.0.0.1",
            "mitre_tag": "T1078",
            "severity": 6.5,
            "tls_metadata": None,
        },
        "label": "T+5s   | [Op 3] Off-hours internal login, ACC-8888 [T1078]",
    },

    # T+12s: brute force (Op 1)
    {
        "offset_seconds": 12,
        "endpoint": "/ingest/cyber",
        "payload": {
            "event_id": "demo-cyber-002",
            "timestamp": None,
            "src_ip": "10.0.0.99",
            "dest_ip": "10.0.0.1",
            "mitre_tag": "T1110",
            "severity": 7.5,
            "tls_metadata": None,
        },
        "label": "T+12s  | [Op 1] 47 failed logins from 10.0.0.99 [T1110]",
    },
    
    # T+18s: Insider malicious command execution (Op 3)
    {
        "offset_seconds": 18,
        "endpoint": "/ingest/cyber",
        "payload": {
            "event_id": "demo-cyber-006",
            "timestamp": None,
            "src_ip": "10.0.0.12",
            "dest_ip": "10.0.0.12",
            "mitre_tag": "T1059",
            "severity": 8.0,
            "tls_metadata": None,
        },
        "label": "T+18s  | [Op 3] PowerShell obfuscated execution on endpoint [T1059]",
    },

    # T+61s: successful login (Op 1)
    {
        "offset_seconds": 61,
        "endpoint": "/ingest/cyber",
        "payload": {
            "event_id": "demo-cyber-003",
            "timestamp": None,
            "src_ip": "10.0.0.99",
            "dest_ip": "10.0.0.1",
            "mitre_tag": "T1078",
            "severity": 8.5,
            "tls_metadata": None,
        },
        "label": "T+61s  | [Op 1] Successful remote login, ACC-0042 [T1078]",
    },

    # ---------------------------------------------------------
    # OPERATION 1: SMURFING EXECUTION
    # ---------------------------------------------------------

    # T+74s: first smurfing transfer
    {
        "offset_seconds": 74,
        "endpoint": "/ingest/transaction",
        "payload": {
            "event_id": "demo-tx-001",
            "timestamp": None,
            "src_ip": "10.0.0.99",
            "account_id": "ACC-0042",
            "dest_account_id": "ACC-0071",
            "amount_inr": 49500.0,
            "fatf_tag": "FATF-3",
            "branch_id": "BR-001",
        },
        "label": "T+74s  | [Op 1] ₹49,500 transfer ACC-0042 → ACC-0071 [FATF-3]",
    },
    
    # T+81s: second smurfing transfer
    {
        "offset_seconds": 81,
        "endpoint": "/ingest/transaction",
        "payload": {
            "event_id": "demo-tx-002",
            "timestamp": None,
            "src_ip": "10.0.0.99",
            "account_id": "ACC-0042",
            "dest_account_id": "ACC-0088",
            "amount_inr": 49500.0,
            "fatf_tag": "FATF-3",
            "branch_id": "BR-001",
        },
        "label": "T+81s  | [Op 1] ₹49,500 transfer ACC-0042 → ACC-0088 [FATF-3]",
    },
    
    # T+89s: third smurfing transfer (receiver is ACC-0103)
    {
        "offset_seconds": 89,
        "endpoint": "/ingest/transaction",
        "payload": {
            "event_id": "demo-tx-003",
            "timestamp": None,
            "src_ip": "10.0.0.99",
            "account_id": "ACC-0042",
            "dest_account_id": "ACC-0103",
            "amount_inr": 49500.0,
            "fatf_tag": "FATF-3",
            "branch_id": "BR-001",
        },
        "label": "T+89s  | [Op 1] ₹49,500 transfer ACC-0042 → ACC-0103 [FATF-3]",
    },

    # T+95s: HNDL quantum risk (Op 1)
    {
        "offset_seconds": 95,
        "endpoint": "/ingest/cyber",
        "payload": {
            "event_id": "demo-cyber-004",
            "timestamp": None,
            "src_ip": "10.0.0.99",
            "dest_ip": "198.51.100.42",
            "mitre_tag": "T1071",
            "severity": 9.0,
            "tls_metadata": {
                "tls_version": "1.2",
                "cipher_suite": "TLS_RSA_WITH_AES_256_CBC_SHA",
                "ja3_hash": "deadbeef1234567890abcdef12345678",
                "ja4_hash": "t12d190900_8d0bba5cdb13_2c6d5c0dbe72",
                "pqc_downgrade_detected": False,
                "session_bytes": 398_458_880,
                "dest_asn": 64512,
            },
        },
        "label": "T+95s  | [Op 1] TLS RSA-2048, 380MB to ASN 64512 [HNDL Quantum Risk]",
    },

    # ---------------------------------------------------------
    # OPERATION 2: MULE LAYERING (Connects to Op 1 via ACC-0103)
    # ---------------------------------------------------------

    # T+110s: Suspicious login to the smurf receiver
    {
        "offset_seconds": 110,
        "endpoint": "/ingest/cyber",
        "payload": {
            "event_id": "demo-cyber-007",
            "timestamp": None,
            "src_ip": "192.168.4.15",
            "dest_ip": "10.0.0.1",
            "mitre_tag": "T1078",
            "severity": 8.5,
            "tls_metadata": None,
        },
        "label": "T+110s | [Op 2] Suspicious login to receiver ACC-0103 from 192.168.4.15 [T1078]",
    },
    
    # T+115s: Layering transfer from ACC-0103 to central mule ACC-0999
    {
        "offset_seconds": 115,
        "endpoint": "/ingest/transaction",
        "payload": {
            "event_id": "demo-tx-004",
            "timestamp": None,
            "src_ip": "192.168.4.15",
            "account_id": "ACC-0103",
            "dest_account_id": "ACC-0999",
            "amount_inr": 48000.0,
            "fatf_tag": "FATF-1",
            "branch_id": "BR-001",
        },
        "label": "T+115s | [Op 2] ₹48,000 transfer ACC-0103 → ACC-0999 [FATF-1 Mule Layering]",
    },
    
    # T+120s: Another layering transfer from ACC-0071 to central mule ACC-0999
    {
        "offset_seconds": 120,
        "endpoint": "/ingest/transaction",
        "payload": {
            "event_id": "demo-tx-005",
            "timestamp": None,
            "src_ip": "192.168.4.15",
            "account_id": "ACC-0071",
            "dest_account_id": "ACC-0999",
            "amount_inr": 48500.0,
            "fatf_tag": "FATF-1",
            "branch_id": "BR-001",
        },
        "label": "T+120s | [Op 2] ₹48,500 transfer ACC-0071 → ACC-0999 [FATF-1 Mule Layering]",
    },

    # ---------------------------------------------------------
    # OPERATION 3: INSIDER EXECUTION (PQC Downgrade)
    # ---------------------------------------------------------

    # T+135s: Massive offshore wire transfer
    {
        "offset_seconds": 135,
        "endpoint": "/ingest/transaction",
        "payload": {
            "event_id": "demo-tx-006",
            "timestamp": None,
            "src_ip": "10.0.0.12",
            "account_id": "ACC-8888",
            "dest_account_id": "ACC-9999-OFFSHORE",
            "amount_inr": 8500000.0,
            "fatf_tag": "FATF-2",
            "branch_id": "BR-001",
        },
        "label": "T+135s | [Op 3] ₹8,500,000 offshore wire from treasury ACC-8888 [FATF-2]",
    },
    
    # T+140s: PQC Downgrade Attack detected
    {
        "offset_seconds": 140,
        "endpoint": "/ingest/cyber",
        "payload": {
            "event_id": "demo-cyber-008",
            "timestamp": None,
            "src_ip": "10.0.0.12",
            "dest_ip": "10.0.0.1",
            "mitre_tag": "T1573",
            "severity": 10.0,
            "tls_metadata": {
                "tls_version": "1.3",
                "cipher_suite": "TLS_AES_128_GCM_SHA256",
                "ja3_hash": "a011a011a011a011a011a011a011a011",
                "ja4_hash": "t13d1516_downgraded_hash",
                "pqc_downgrade_detected": True,
                "session_bytes": 10240,
                "dest_asn": 0,
            },
        },
        "label": "T+140s | [Op 3] PQC Downgrade Attack detected during internal session [T1573]",
    },
]


def build_demo_scenario_json(start_time: datetime) -> list[dict]:
    """Returns the scenario as a list of dicts with real timestamps for static export."""
    events = []
    for e in DEMO_EVENTS:
        ev = dict(e)
        ts = start_time.timestamp() + e["offset_seconds"]
        ev["payload"] = dict(e["payload"])
        ev["payload"]["timestamp"] = datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
        events.append(ev)
    return events


def main():
    parser = argparse.ArgumentParser(description="Run the Smurfing Phantom demo scenario")
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--fast", action="store_true", help="Skip real-time delays")
    parser.add_argument("--api-key", default=None)
    args = parser.parse_args()

    import os
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
    api_key = args.api_key or os.getenv("API_KEY", "changeme")

    start_time = datetime.now(tz=timezone.utc)
    prev_offset = 0

    # Save static scenario JSON for submission
    scenario = build_demo_scenario_json(start_time)
    (SAMPLE_DIR / "demo_scenario.json").write_text(json.dumps(scenario, indent=2))
    print(f"Scenario saved → sample_data/demo_scenario.json\n")
    print("=" * 60)
    print("  Operation Smurfing Phantom | HarvestGuard Demo")
    print("=" * 60)

    headers = {"X-API-Key": api_key, "Content-Type": "application/json"}

    with httpx.Client(base_url=args.base_url, timeout=15) as client:
        for event in DEMO_EVENTS:
            # Real-time pacing (skip if --fast)
            if not args.fast:
                wait = event["offset_seconds"] - prev_offset
                if wait > 0:
                    time.sleep(wait)
            prev_offset = event["offset_seconds"]

            payload = dict(event["payload"])
            payload["timestamp"] = datetime.now(tz=timezone.utc).isoformat()

            try:
                resp = client.post(event["endpoint"], json=payload, headers=headers)
                status = "✓" if resp.status_code == 202 else f"✗ {resp.status_code}"
            except httpx.ConnectError:
                status = "✗ connection refused. Is the API running?"

            print(f"{status}  {event['label']}")

    print("\nDemo scenario complete. Watch the dashboard for correlated alerts.")


if __name__ == "__main__":
    main()
