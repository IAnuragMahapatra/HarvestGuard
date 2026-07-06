"""Ingestion routes for /ingest/cyber and /ingest/transaction."""

import logging

from fastapi import APIRouter, BackgroundTasks, Depends, Request, HTTPException
from fastapi.responses import JSONResponse

from src.api.models import CyberEvent, TransactionEvent
from src.core import audit
from src.core.quantum_monitor import score_tls

logger = logging.getLogger("ingest")
router = APIRouter()


def _get_state(request: Request):
    return request.app.state


@router.post("/ingest/cyber", status_code=202)
async def ingest_cyber(
    event: CyberEvent,
    background: BackgroundTasks,
    request: Request,
):
    state = _get_state(request)
    event_dict = event.model_dump()
    event_dict["type"] = "cyber"

    # TLS quantum risk: score synchronously so it's in Redis before correlation
    tls_meta = event_dict.get("tls_metadata")
    if tls_meta:
        event_dict["tls_risk_score"] = score_tls(tls_meta)

    await audit.log("/ingest/cyber", event.src_ip, event.event_id)
    await state.db.write_event(event_dict)
    await state.correlator.ingest_event(event_dict)

    return JSONResponse({"status": "accepted", "event_id": event.event_id}, status_code=202)


@router.post("/ingest/transaction", status_code=202)
async def ingest_transaction(
    event: TransactionEvent,
    background: BackgroundTasks,
    request: Request,
):
    state = _get_state(request)
    event_dict = event.model_dump()
    event_dict["type"] = "transaction"

    await audit.log("/ingest/transaction", event.src_ip, event.event_id)
    await state.db.write_event(event_dict)
    await state.correlator.ingest_event(event_dict)

    return JSONResponse({"status": "accepted", "event_id": event.event_id}, status_code=202)
