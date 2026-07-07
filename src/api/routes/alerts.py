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


@router.get("/alerts/{alert_id}/graph")
async def get_alert_graph(alert_id: str, request: Request):
    state = request.app.state
    alert = await state.db.get_alert(alert_id)
    if not alert:
        return JSONResponse({"error": "not found"}, status_code=404)
    
    from src.ml.graph_model import graph_nodes_for_alert
    
    account_id = alert.get("account_id")
    src_ip = alert.get("src_ip")
    
    # If we don't have account/IP, return empty graph
    if not account_id and not src_ip:
        return {"nodes": [], "edges": []}
        
    graph_data = graph_nodes_for_alert([account_id] if account_id else [], src_ip)
    return graph_data

