"""Audit log writer. Every ingestion request gets a line here."""

import asyncio
import logging
from datetime import datetime, timezone
from pathlib import Path

_log_path = Path("audit.log")
_lock = asyncio.Lock()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("audit")


async def log(endpoint: str, src_ip: str, event_id: str) -> None:
    ts = datetime.now(tz=timezone.utc).isoformat()
    line = f"{ts} | {endpoint} | {src_ip} | {event_id}\n"
    async with _lock:
        with open(_log_path, "a", encoding="utf-8") as f:
            f.write(line)
