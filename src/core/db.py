"""
SQLite database layer. All writes use parameterised queries.
Accessed via aiosqlite for non-blocking I/O inside FastAPI.
"""

import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import aiosqlite

logger = logging.getLogger("db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
    event_id    TEXT PRIMARY KEY,
    timestamp   TEXT NOT NULL,
    type        TEXT NOT NULL,
    src_ip      TEXT,
    account_id  TEXT,
    raw_json    TEXT,
    created_at  TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS alerts (
    alert_id            TEXT PRIMARY KEY,
    created_at          TEXT NOT NULL,
    src_ip              TEXT,
    account_id          TEXT,
    anomaly_score       REAL NOT NULL,
    tls_risk_score      REAL DEFAULT 0.0,
    shap_values         TEXT,
    shap_waterfall_png  TEXT,
    llm_report          TEXT,
    llm_source          TEXT DEFAULT 'template',
    threat_chain        TEXT,
    is_fraud_ring       INTEGER DEFAULT 0,
    ring_members        TEXT,
    mitre_tags          TEXT,
    fatf_tags           TEXT
);

CREATE TABLE IF NOT EXISTS audit_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp   TEXT NOT NULL,
    endpoint    TEXT NOT NULL,
    src_ip      TEXT,
    event_id    TEXT
);

CREATE INDEX IF NOT EXISTS idx_alerts_created ON alerts (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_events_src_ip   ON events  (src_ip);
CREATE INDEX IF NOT EXISTS idx_events_account  ON events  (account_id);
"""


class DatabaseWriter:
    def __init__(self, db_path: str, ml_inference, ml_explain, ml_graph, ml_llm):
        self.db_path = db_path
        self.infer = ml_inference
        self.explain = ml_explain
        self.graph = ml_graph
        self.llm = ml_llm

    async def init_schema(self) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.executescript(SCHEMA)
            await db.commit()

    async def write_event(self, event: dict) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """INSERT OR REPLACE INTO events
                   (event_id, timestamp, type, src_ip, account_id, raw_json)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    event.get("event_id", str(uuid.uuid4())),
                    event.get("timestamp", ""),
                    event.get("type", "unknown"),
                    event.get("src_ip", ""),
                    event.get("account_id", ""),
                    json.dumps(event),
                ),
            )
            await db.commit()

    async def write_fused_and_score(self, vector: dict, raw_events: list[dict]) -> None:
        """Score the fused vector and persist an alert if above threshold."""
        try:
            score = self.infer.score(vector)
        except Exception as exc:
            logger.error("Inference error: %s", exc)
            return

        tls_risk = vector.get("tls_risk_score", 0.0)
        is_quantum_alert = tls_risk >= 0.5

        if score < 0.75 and not is_quantum_alert:
            return

        # SHAP explanation
        shap_dict = self.explain.shap_values(vector)
        shap_png = self.explain.waterfall_png(shap_dict)

        # Fraud ring lookup
        account_id = vector.get("_account_id", "")
        ring_info = self.graph.ring_lookup(account_id) if account_id else {}

        # LLM report
        mitre_tags = vector.get("_mitre_tags", [])
        fatf_tags = vector.get("_fatf_tags", [])
        alert_data = {
            "src_ip": vector.get("_src_ip", ""),
            "account_id": account_id,
            "anomaly_score": score,
            "tls_risk_score": tls_risk,
            "mitre_tags": mitre_tags,
            "fatf_tags": fatf_tags,
        }
        llm_text, llm_source = self.llm.generate(alert_data, shap_dict)

        alert_id = str(uuid.uuid4())
        now = datetime.now(tz=timezone.utc).isoformat()

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """INSERT INTO alerts
                   (alert_id, created_at, src_ip, account_id, anomaly_score,
                    tls_risk_score, shap_values, shap_waterfall_png,
                    llm_report, llm_source, threat_chain,
                    is_fraud_ring, ring_members, mitre_tags, fatf_tags)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    alert_id, now,
                    vector.get("_src_ip", ""), account_id, score,
                    tls_risk,
                    json.dumps(shap_dict), shap_png,
                    llm_text, llm_source,
                    json.dumps(vector.get("_threat_chain", [])),
                    int(ring_info.get("is_fraud_ring", False)),
                    json.dumps(ring_info.get("ring_members", [])),
                    json.dumps(mitre_tags),
                    json.dumps(fatf_tags),
                ),
            )
            await db.commit()

        logger.info("Alert written: %s score=%.3f tls=%.2f ring=%s",
                    alert_id, score, tls_risk, ring_info.get("is_fraud_ring"))

    async def get_alerts(self, limit: int = 50, since_id: Optional[str] = None) -> list[dict]:
        query = "SELECT * FROM alerts ORDER BY created_at DESC LIMIT ?"
        params: list = [limit]
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
        return [_row_to_dict(row) for row in rows]

    async def get_alert(self, alert_id: str) -> Optional[dict]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM alerts WHERE alert_id = ?", (alert_id,)
            ) as cursor:
                row = await cursor.fetchone()
        return _row_to_dict(row) if row else None

    async def get_counts(self) -> dict:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT COUNT(*) FROM events WHERE type='transaction'") as c:
                tx_count = (await c.fetchone())[0]
            async with db.execute("SELECT COUNT(*) FROM events WHERE type='cyber'") as c:
                cyber_count = (await c.fetchone())[0]
            async with db.execute("SELECT COUNT(*) FROM alerts") as c:
                alert_count = (await c.fetchone())[0]
            async with db.execute(
                "SELECT COUNT(*) FROM alerts WHERE tls_risk_score >= 0.5"
            ) as c:
                quantum_count = (await c.fetchone())[0]
        return {
            "transactions_analysed": tx_count,
            "cyber_events_ingested": cyber_count,
            "correlated_threats": alert_count,
            "quantum_risk_flags": quantum_count,
        }


def _row_to_dict(row) -> dict:
    d = dict(row)
    for field in ("shap_values", "threat_chain", "ring_members", "mitre_tags", "fatf_tags"):
        if d.get(field):
            try:
                d[field] = json.loads(d[field])
            except (json.JSONDecodeError, TypeError):
                pass
    d["is_fraud_ring"] = bool(d.get("is_fraud_ring", 0))
    return d
