"""
HarvestGuard Streamlit dashboard — Command Center + Alert Detail.

Run: uv run streamlit run src/ui/app.py
"""

import os

import httpx
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from src.ml import graph_model as gm
from src.ui.components import alert_feed, graph_view, shap_view, threat_chain


@st.cache_resource
def _load_graph_model():
    try:
        gm.load_embeddings()
    except FileNotFoundError:
        pass  # run generate_baseline.py first
    return gm

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")
API_KEY = os.getenv("API_KEY", "changeme")
HEADERS = {"X-API-Key": API_KEY}

CRIMSON = "#E53935"
AMBER = "#FFB300"
BLUE = "#29B6F6"
EMERALD = "#00E676"
GHOST = "#8892A4"

st.set_page_config(
    page_title="HarvestGuard — Threat Correlation",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Global CSS
st.markdown("""
<style>
  .block-container { padding-top: 1rem; padding-bottom: 0.5rem; }
  .stMetric label { font-size: 0.75rem !important; color: #8892A4 !important; }
  .stMetric .css-1wivap2 { font-size: 1.6rem !important; }
  div[data-testid="stHorizontalBlock"] { gap: 0.5rem; }
</style>
""", unsafe_allow_html=True)


def _get(path: str) -> dict | list | None:
    try:
        r = httpx.get(f"{API_BASE}{path}", headers=HEADERS, timeout=4)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None


def _metric_tile(label: str, value: int, prev: int, colour: str):
    delta = value - prev if prev is not None else None
    st.markdown(
        f'<div style="background:#1E2430;border-left:3px solid {colour};'
        f'padding:12px 16px;border-radius:6px">'
        f'<div style="font-size:0.72rem;color:#8892A4">{label}</div>'
        f'<div style="font-size:2rem;font-weight:700;color:{colour}">{value:,}</div>'
        + (f'<div style="font-size:0.72rem;color:#8892A4">+{delta} this refresh</div>' if delta else "")
        + "</div>",
        unsafe_allow_html=True,
    )


def page_command_center():
    # Auto-refresh every 2 seconds
    st_autorefresh(interval=2000, key="cmd_refresh")

    counts = _get("/counts") or {}
    prev = st.session_state.get("prev_counts", {})

    # ── KPI row ───────────────────────────────────────────────────────
    st.markdown(
        '<h2 style="margin:0 0 12px 0">⚡ HarvestGuard <span style="font-size:1rem;'
        'font-weight:400;color:#8892A4">— Real-time Cyber-Fraud Correlation</span></h2>',
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        _metric_tile("Transactions Analysed", counts.get("transactions_analysed", 0), prev.get("transactions_analysed"), EMERALD)
    with c2:
        _metric_tile("Cyber Events Ingested", counts.get("cyber_events_ingested", 0), prev.get("cyber_events_ingested"), BLUE)
    with c3:
        _metric_tile("Correlated Threats", counts.get("correlated_threats", 0), prev.get("correlated_threats"), CRIMSON)
    with c4:
        _metric_tile("Quantum Risk Flags", counts.get("quantum_risk_flags", 0), prev.get("quantum_risk_flags"), BLUE)

    st.session_state.prev_counts = counts
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Main split: alert feed (60%) + graph (40%) ───────────────────
    left, right = st.columns([6, 4])

    with left:
        st.markdown("### 🚨 Live Alert Feed")
        alerts = _get("/alerts?limit=50") or []
        st.session_state.cached_alerts = alerts
        alert_feed.render(alerts)

    with right:
        st.markdown("### 🕸 Network Threat Graph")
        # Build graph from latest alert if available
        _gm = _load_graph_model()
        if alerts:
            latest = alerts[0]
            account_ids = (
                [latest.get("account_id")] + (latest.get("ring_members") or [])
                if latest.get("account_id")
                else []
            )
            graph_data = _gm.graph_nodes_for_alert(
                [a for a in account_ids if a], latest.get("src_ip", "")
            )
        else:
            graph_data = {"nodes": [], "edges": []}

        graph_view.render(graph_data)

        st.caption(
            f'<span style="color:{GHOST}">Graph updates on each new alert. '
            f"Nodes are draggable — hover for details.</span>",
            unsafe_allow_html=True,
        )


def page_alert_detail():
    alert_id = st.session_state.get("selected_alert_id")
    if not alert_id:
        st.session_state.page = "command_center"
        st.rerun()

    if st.button("← Back to Command Center"):
        st.session_state.page = "command_center"
        st.session_state.selected_alert_id = None
        st.rerun()

    alert = _get(f"/alerts/{alert_id}")
    if not alert:
        st.error("Alert not found.")
        return

    score = alert.get("anomaly_score", 0)
    tls = alert.get("tls_risk_score", 0)
    account = alert.get("account_id", "—")
    src_ip = alert.get("src_ip", "—")
    ring = alert.get("is_fraud_ring", False)

    score_colour = CRIMSON if score >= 0.90 else AMBER
    st.markdown(
        f'<h2 style="margin:0 0 4px 0">Alert Detail '
        f'<span style="color:{score_colour};font-size:1rem">score {score:.2f}</span>'
        + (f' <span style="color:{BLUE};font-size:0.9rem">🔐 QUANTUM RISK {tls:.2f}</span>' if tls >= 0.5 else "")
        + (f' <span style="color:{AMBER};font-size:0.9rem">🕸 FRAUD RING</span>' if ring else "")
        + f'</h2><div style="color:{GHOST};font-size:0.8rem">IP: {src_ip} | Account: {account} | {alert.get("created_at","")[:19].replace("T"," ")}</div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    left, right = st.columns([55, 45])

    with left:
        st.markdown("#### 🔗 Threat Chain")
        chain = alert.get("threat_chain") or []
        threat_chain.render(chain, alert)
        st.markdown("<br>", unsafe_allow_html=True)

    with right:
        shap_view.render(alert)


# ── Router ────────────────────────────────────────────────────────────────────

if "page" not in st.session_state:
    st.session_state.page = "command_center"
if "selected_alert_id" not in st.session_state:
    st.session_state.selected_alert_id = None

if st.session_state.page == "detail" and st.session_state.selected_alert_id:
    page_alert_detail()
else:
    page_command_center()
