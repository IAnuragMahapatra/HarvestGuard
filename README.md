# HarvestGuard ⚡

HarvestGuard connects a bank's Security Operations Center (SOC) with its Fraud Detection team in real time. It takes in cybersecurity telemetry and transaction data together, correlates them across a sliding time window, and raises composite alerts that neither team would catch on their own. Each alert comes with a full explanation in under 5 seconds, before the money moves.

Built for **FINSPARK'26**, organised by Bank of Maharashtra at COEP Technological University, Pune.

## The Problem

Banks work in two separate silos. The SOC tracks network intrusions and credential attacks. The fraud team tracks transaction anomalies. An attacker who runs credential stuffing on the cyber side and then makes just-below-threshold transfers on the financial side produces low-severity alerts in both systems and escalates in neither. HarvestGuard sees both signals, joins them, and raises one alert with a full explanation.

## What Makes This Different

| Capability | What it does |
| :--- | :--- |
| **Cross-framework correlation** | Maps MITRE ATT&CK cyber events to FATF Financial Crime Typologies in one pipeline |
| **GNN Fraud Ring Detection** | Pre-trained GraphSAGE embeddings spot multi-hop mule account networks |
| **HNDL Quantum Risk Monitor** | Catches Harvest-Now-Decrypt-Later patterns via TLS fingerprint and volume checks |
| **Local LLM SOC Reports** | Phi-3-mini writes 3-5 sentence incident reports on-device, data stays on the bank's servers |
| **Threat Chain View** | One-screen timeline of the full cyber to transaction attack chain |

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- Docker Desktop (for Redis)

## Quickstart

```bash
# 1. Clone and configure
cp .env.example .env

# 2. Start Redis
docker compose up -d redis

# 3. Generate baseline data and train models
uv run python src/scripts/generate_baseline.py

# 4. Start the API (in one terminal)
uv run uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# 5. Start the dashboard (in another terminal)
uv run streamlit run src/ui/app.py
```

**Windows users:** You can run all of the above steps with a single script:

```powershell
.\run.ps1
```

Open [http://localhost:8501](http://localhost:8501) to see the Command Center dashboard.

## Running the Demo Scenario

With the API running, inject the "Operation Smurfing Phantom" attack chain:

```bash
uv run python src/scripts/run_demo.py
```

Use `--fast` to skip real-time pacing:

```bash
uv run python src/scripts/run_demo.py --fast
```

Watch the dashboard. Within 5 seconds of the first transfer event, a correlated alert shows up with:

- The full cyber to transaction attack chain (Threat Chain view)
- SHAP waterfall explaining which features drove the anomaly score
- A generated SOC incident report
- Fraud ring membership for the target accounts
- A separate Quantum Risk alert for the HNDL TLS session

## Architecture

```text
Scripts (generate_baseline.py / run_demo.py)
  |
  v
POST /ingest/cyber  or  /ingest/transaction
  |
  +-- API Key check (X-API-Key header)
  +-- Pydantic validate
  +-- Audit log write
  |
  +----------------------+
  v                      v
Redis TTL store    Quantum Monitor
(sliding window)   (TLS events only)
  |                      |
  |<-- tls_risk_score ---+
  v
Correlation Engine (cross-type join)
  v
Fused Feature Vector
  v
Isolation Forest (anomaly score >= 0.75 triggers alert)
  v
SHAP explain -> GNN ring lookup -> LLM SOC report
  v
SQLite alert write
  v
Streamlit dashboard (2s polling)
```

**Storage:** Redis for the ephemeral sliding window, SQLite for persistent alerts. No Elasticsearch.

## Security Practices

| Practice | Implementation |
| :--- | :--- |
| Authentication | `X-API-Key` header required on all ingestion endpoints |
| Secret management | `.env` file is gitignored; `.env.example` committed with placeholder values |
| SQL injection prevention | `aiosqlite` parameterised queries throughout, no f-string SQL |
| Error exposure | Structured JSON errors returned, no stack traces exposed to callers |
| Audit trail | Every ingestion request logged with timestamp, endpoint, IP and event ID |
| Container security | Docker containers run as non-root user (`USER finspark`) |
| Input validation | Pydantic models enforce types and ranges at the API boundary |
| Dependency pinning | `uv.lock` committed for reproducible builds |

## Tech Stack

| Layer | Choice |
| :--- | :--- |
| Backend | Python 3.11+, FastAPI, Uvicorn |
| Sliding Window | Redis 7 |
| Database | SQLite via aiosqlite |
| Anomaly Detection | Scikit-Learn Isolation Forest |
| Fraud Ring Detection | PyTorch Geometric (GraphSAGE, pre-trained embeddings) |
| Explainability | SHAP |
| LLM SOC Reports | llama.cpp + Phi-3-mini-4k-instruct (Q4_K_M, local) |
| Frontend | Streamlit + streamlit-echarts |
| Deployment | Docker + docker-compose |
| Data Generation | Faker + custom Python scripts |
| Package Manager | uv |

All dependencies carry OSI-approved open-source licences.

## APIs Used (Submission Disclosure)

- FastAPI
- Redis (via redis-py)
- llama.cpp (via llama-cpp-python, if model is downloaded)
- PyTorch Geometric
- SHAP
- Streamlit + streamlit-echarts

## Team

| Module | Owner |
| :--- | :--- |
| `src/ml/`, `src/scripts/`, `sample_data/` | Srinibas Das |
| `src/api/`, `src/core/`, `docker-compose.yml` | Anurag Mahapatra |
| `src/ui/`, `src/ml/llm_reporter.py` | Ayush Kishan |
| `README.md`, `pyproject.toml`, `Dockerfile`, docs | Narayan Agarwal |
