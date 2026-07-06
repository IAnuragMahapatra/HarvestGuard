"""
Event correlation engine.

On every ingested event, queries Redis for cross-type events in the sliding
window and builds a Fused Feature Vector for the ML pipeline.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

import redis.asyncio as aioredis

from src.core.quantum_monitor import explain_tls

logger = logging.getLogger("correlator")

MITRE_TAG_MAP = {
    "T1046": 1046, "T1059": 1059, "T1071": 1071,
    "T1078": 1078, "T1110": 1110, "T1133": 1133,
    "T1190": 1190, "T1566": 1566,
}

IP_BLOCKLIST = {
    "10.0.0.99",   # demo attacker IP, always flagged
}


class CorrelationEngine:
    def __init__(self, redis_client: aioredis.Redis, window_seconds: int, db_writer):
        self.redis = redis_client
        self.window = window_seconds
        self.db = db_writer

    async def ingest_event(self, event: dict) -> None:
        """Store event in Redis and attempt correlation."""
        src_ip = event.get("src_ip", "")
        account_id = event.get("account_id", "")
        event_id = event.get("event_id", str(uuid.uuid4()))
        event_type = event.get("type", "unknown")

        # TTL-keyed storage, one key per event
        key = f"event:{src_ip}:{account_id}:{event_id}"
        await self.redis.setex(key, self.window, json.dumps(event))

        # async correlation, don't block the ingest response
        asyncio.create_task(self._correlate(src_ip, account_id, event_type, event))

    async def _correlate(
        self, src_ip: str, account_id: str, trigger_type: str, trigger_event: dict
    ) -> None:
        try:
            # dedup: only one alert per IP+account per window
            dedup_key = f"alert_lock:{src_ip}:{account_id}"
            if await self.redis.exists(dedup_key):
                return

            window_events = await self._fetch_window_events(src_ip, account_id)
            if len(window_events) < 2:
                return

            cyber_events = [e for e in window_events if e.get("type") == "cyber"]
            tx_events = [e for e in window_events if e.get("type") == "transaction"]

            # need at least one of each type to produce a fused vector
            if not cyber_events or not tx_events:
                return

            vector = self._build_fused_vector(cyber_events, tx_events)

            # score first so we know if this is worth writing
            try:
                alert_score = self.infer.score(vector)
            except RuntimeError:
                return

            tls_risk = vector.get("tls_risk_score", 0.0)
            if alert_score < 0.75 and tls_risk < 0.5:
                return

            # set the dedup lock before the async DB write so concurrent tasks don't double-fire
            await self.redis.setex(dedup_key, 60, "1")
            await self.db.write_fused_and_score(vector, window_events)

        except Exception:
            logger.exception("Correlation error for ip=%s account=%s", src_ip, account_id)

    async def _fetch_window_events(self, src_ip: str, account_id: str) -> list[dict]:
        """Scan Redis for all events matching this IP or account in the window."""
        patterns = set()
        if src_ip:
            patterns.add(f"event:{src_ip}:*")
        if account_id:
            patterns.add(f"event:*:{account_id}:*")

        keys = set()
        for pattern in patterns:
            async for key in self.redis.scan_iter(pattern):
                keys.add(key)

        events = []
        for key in keys:
            raw = await self.redis.get(key)
            if raw:
                try:
                    events.append(json.loads(raw))
                except json.JSONDecodeError:
                    pass

        return events

    def _build_fused_vector(
        self, cyber_events: list[dict], tx_events: list[dict]
    ) -> dict:
        now = datetime.now(tz=timezone.utc).timestamp()

        # use the pre-scored tls_risk_score stored on each event (set by the ingest route)
        tls_risk_score = max(
            (e.get("tls_risk_score", 0.0) for e in cyber_events), default=0.0
        )

        # Transaction velocity over last 3 minutes
        tx_3min = [
            e for e in tx_events
            if self._seconds_ago(e.get("timestamp", ""), now) <= 180
        ]
        velocity_3min = sum(e.get("amount_inr", 0) for e in tx_3min)

        # IP reputation: 0.0 = flagged, 1.0 = clean
        src_ip = cyber_events[0].get("src_ip", "")
        ip_rep = 0.0 if src_ip in IP_BLOCKLIST else 0.9

        # Time delta from first cyber to first transaction
        cyber_ts = sorted(
            (self._to_ts(e.get("timestamp", "")) for e in cyber_events)
        )
        tx_ts = sorted(
            (self._to_ts(e.get("timestamp", "")) for e in tx_events)
        )
        time_delta = max(0.0, (tx_ts[0] - cyber_ts[0]) if cyber_ts and tx_ts else 9999)

        # Highest MITRE tag (as int)
        mitre_ints = [
            MITRE_TAG_MAP.get(e.get("mitre_tag", ""), 0) for e in cyber_events
        ]
        top_mitre = max(mitre_ints) if mitre_ints else 0

        # FATF tag from transactions (take highest numeric suffix)
        fatf_tags = [e.get("fatf_tag") for e in tx_events if e.get("fatf_tag")]
        fatf_int = 0
        for tag in fatf_tags:
            try:
                fatf_int = max(fatf_int, int(str(tag).split("-")[-1]))
            except (ValueError, IndexError):
                pass

        return {
            "prior_cyber_alert_count": len(cyber_events),
            "max_cyber_severity": max(
                (e.get("severity", 0) for e in cyber_events), default=0
            ),
            "transaction_count_3min": len(tx_3min),
            "transfer_velocity_3min": velocity_3min,
            "ip_reputation_score": ip_rep,
            "time_delta_cyber_to_tx": time_delta,
            "tls_risk_score": tls_risk_score,
            "mitre_tag": top_mitre,
            "fatf_tag": fatf_int,
            # Metadata passed through for alert building (not used as ML features)
            "_src_ip": src_ip,
            "_account_id": tx_events[0].get("account_id", "") if tx_events else "",
            "_mitre_tags": [e.get("mitre_tag", "") for e in cyber_events],
            "_fatf_tags": fatf_tags,
            "_threat_chain": sorted(
                cyber_events + tx_events,
                key=lambda e: e.get("timestamp", ""),
            ),
            "_tls_metadata": next(
                (e.get("tls_metadata") for e in cyber_events if e.get("tls_metadata")),
                None,
            ),
        }

    @staticmethod
    def _to_ts(ts_str: str) -> float:
        try:
            return datetime.fromisoformat(ts_str.replace("Z", "+00:00")).timestamp()
        except (ValueError, AttributeError):
            return 0.0

    @staticmethod
    def _seconds_ago(ts_str: str, now: float) -> float:
        ts = CorrelationEngine._to_ts(ts_str)
        return max(0.0, now - ts)
