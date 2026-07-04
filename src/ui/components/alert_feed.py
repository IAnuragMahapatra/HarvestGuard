"""Alert feed component — scrolling colour-coded table of recent alerts."""

import streamlit as st

CRIMSON = "#E53935"
AMBER = "#FFB300"
BLUE = "#29B6F6"
SLATE = "#1E2430"
GHOST = "#8892A4"


def _row_colour(alert: dict) -> str:
    if alert.get("tls_risk_score", 0) >= 0.5:
        return BLUE
    if alert.get("anomaly_score", 0) >= 0.90:
        return CRIMSON
    return AMBER


def _severity_badge(score: float, tls: float) -> str:
    if tls >= 0.5:
        return "🔐 QUANTUM"
    if score >= 0.90:
        return "🔴 CRITICAL"
    return "🟠 HIGH"


def render(alerts: list[dict]) -> None:
    """Render the live alert feed. Clicking a row sets session state to navigate to detail."""

    # Pulse animation for critical rows
    st.markdown("""
    <style>
    @keyframes pulse-red {
      0%   { background-color: rgba(229,57,53,0.18); }
      50%  { background-color: rgba(229,57,53,0.35); }
      100% { background-color: rgba(229,57,53,0.18); }
    }
    @keyframes pulse-blue {
      0%   { background-color: rgba(41,182,246,0.12); }
      50%  { background-color: rgba(41,182,246,0.28); }
      100% { background-color: rgba(41,182,246,0.12); }
    }
    .alert-critical { animation: pulse-red  2s infinite; border-radius: 6px; padding: 2px 6px; }
    .alert-quantum  { animation: pulse-blue 2s infinite; border-radius: 6px; padding: 2px 6px; }
    .alert-high     { background-color: rgba(255,179,0,0.12); border-radius: 6px; padding: 2px 6px; }
    </style>
    """, unsafe_allow_html=True)

    if not alerts:
        st.info("No alerts yet. Run `python src/scripts/run_demo.py` to inject the demo scenario.")
        return

    st.markdown(f"**{len(alerts)} recent alerts** — click any row to view details")

    for alert in alerts:
        score = alert.get("anomaly_score", 0)
        tls = alert.get("tls_risk_score", 0)
        colour = _row_colour(alert)
        badge = _severity_badge(score, tls)
        created = alert.get("created_at", "")[:19].replace("T", " ")
        mitre = ", ".join(alert.get("mitre_tags") or []) or "—"
        fatf = ", ".join(alert.get("fatf_tags") or []) or "—"
        account = alert.get("account_id") or "—"
        ring_icon = " 🕸" if alert.get("is_fraud_ring") else ""

        css_class = (
            "alert-quantum" if tls >= 0.5
            else "alert-critical" if score >= 0.90
            else "alert-high"
        )

        col1, col2, col3, col4, col5, col6 = st.columns([2, 1.2, 1.8, 1.8, 1.5, 1])
        with col1:
            st.markdown(f'<div class="{css_class}">{created}</div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<span style="color:{colour};font-weight:700">{badge}</span>', unsafe_allow_html=True)
        with col3:
            st.caption(mitre)
        with col4:
            st.caption(fatf)
        with col5:
            st.caption(f"{account}{ring_icon}")
        with col6:
            if st.button("→", key=f"alert_btn_{alert['alert_id']}", help="View details"):
                st.session_state.selected_alert_id = alert["alert_id"]
                st.session_state.page = "detail"
                st.rerun()

        st.markdown('<hr style="margin:2px 0;border-color:#1E2430">', unsafe_allow_html=True)
