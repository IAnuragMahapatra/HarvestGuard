"""Alert query routes for /alerts and /alerts/{alert_id}."""

import logging

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger("alerts")
router = APIRouter()


@router.get("/alerts")
async def list_alerts(request: Request, limit: int = 50):
    state = request.app.state
    alerts = await state.db.get_alerts(limit=min(limit, 200))
    # strip waterfall PNG from list view, too large for polling
    for a in alerts:
        a.pop("shap_waterfall_png", None)
    return alerts


@router.get("/alerts/{alert_id}")
async def get_alert(alert_id: str, request: Request):
    state = request.app.state
    alert = await state.db.get_alert(alert_id)
    if not alert:
        return JSONResponse({"error": "not found"}, status_code=404)
    return alert


@router.get("/counts")
async def get_counts(request: Request):
    return await request.app.state.db.get_counts()
