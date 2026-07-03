"""
FastAPI entry point for HarvestGuard.

Startup: loads models, connects Redis, initialises SQLite schema.
Middleware: API key auth on all /ingest/* endpoints.
"""

import logging
import os
from contextlib import asynccontextmanager

import redis.asyncio as aioredis
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.api.routes import alerts as alerts_router
from src.api.routes import ingest as ingest_router
from src.core.correlator import CorrelationEngine
from src.core.db import DatabaseWriter
from src.ml import explain, graph_model, inference, llm_reporter

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger("main")

API_KEY = os.getenv("API_KEY", "changeme")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
DB_PATH = os.getenv("DB_PATH", "finspark.db")
WINDOW_SECONDS = int(os.getenv("WINDOW_SECONDS", "600"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Models ──────────────────────────────────────────────────────────
    try:
        inference.load_model()
        logger.info("Isolation Forest loaded")
    except FileNotFoundError:
        logger.warning("isolation_forest.pkl not found — run generate_baseline.py first")

    try:
        graph_model.load_embeddings()
        logger.info("GNN embeddings loaded")
    except FileNotFoundError:
        logger.warning("graph_embeddings.pkl not found — fraud ring detection disabled")

    llm_reporter.load_llm()

    # ── Redis ────────────────────────────────────────────────────────────
    redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)

    # ── Database ─────────────────────────────────────────────────────────
    db = DatabaseWriter(DB_PATH, inference, explain, graph_model, llm_reporter)
    await db.init_schema()

    # ── Correlator ───────────────────────────────────────────────────────
    correlator = CorrelationEngine(redis_client, WINDOW_SECONDS, db)

    app.state.db = db
    app.state.correlator = correlator
    app.state.redis = redis_client

    logger.info("HarvestGuard API ready — window=%ds db=%s", WINDOW_SECONDS, DB_PATH)
    yield

    await redis_client.aclose()


app = FastAPI(
    title="HarvestGuard",
    description="Real-time cyber-fraud correlation for banking SOC and fraud teams",
    version="0.1.0",
    lifespan=lifespan,
)

PROTECTED_PREFIXES = ("/ingest/",)


@app.middleware("http")
async def api_key_middleware(request: Request, call_next):
    """Reject unauthenticated ingestion requests with a plain 401."""
    if any(request.url.path.startswith(p) for p in PROTECTED_PREFIXES):
        key = request.headers.get("X-API-Key", "")
        if key != API_KEY:
            return JSONResponse({"error": "Unauthorized"}, status_code=401)
    return await call_next(request)


@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s", request.url.path)
    return JSONResponse({"error": "Internal server error"}, status_code=500)


app.include_router(ingest_router.router)
app.include_router(alerts_router.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
