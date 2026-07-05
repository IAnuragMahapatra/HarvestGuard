"""
Threat Chain timeline view — the primary differentiator.

Horizontal echarts timeline showing every event in an alert's correlation
window, colour-coded by type, with MITRE and FATF labels.
"""

import streamlit as st
from streamlit_echarts import st_echarts

CRIMSON = "#E53935"
AMBER = "#FFB300"
BLUE = "#29B6F6"
EMERALD = "#00E676"
GHOST = "#8892A4"

TYPE_COLOUR = {
    "cyber": BLUE,
    "transaction": AMBER,
    "quantum": CRIMSON,
}

TYPE_ICON = {
    "cyber": "⚡",
    "transaction": "💸",
    "quantum": "🔐",
}


def _event_type(event: dict) -> str:
    if event.get("tls_metadata") or event.get("tls_risk_score", 0) >= 0.5:
        return "quantum"
    return event.get("type", "cyber")


def _short_label(event: dict) -> str:
    etype = _event_type(event)
    if etype == "transaction":
        amount = event.get("amount_inr", 0)
        dest = event.get("dest_account_id", "")
        fatf = event.get("fatf_tag") or ""
        return f"₹{amount:,.0f} → {dest}" + (f"\n[{fatf}]" if fatf else "")
    if etype == "quantum":
        return f"TLS Risk\n{event.get('mitre_tag', 'T1071')}"
    return f"{event.get('mitre_tag', '')}\nseverity {event.get('severity', 0):.1f}"


def render(threat_chain: list[dict], alert: dict) -> None:
    if not threat_chain:
        st.info("No threat chain data for this alert.")
        return

    # Build MITRE→FATF label for the header
    mitre_tags = [e.get("mitre_tag", "") for e in threat_chain if e.get("mitre_tag")]
    fatf_tags = [e.get("fatf_tag", "") for e in threat_chain if e.get("fatf_tag")]
    chain_label = " → ".join(filter(None, mitre_tags[:4]))
    if fatf_tags:
        chain_label += " → " + " → ".join(fatf_tags[:2])

    st.markdown(
        f'<div style="font-size:0.8rem;color:{GHOST};margin-bottom:4px">'
        f"🔗 Attack chain: <strong>{chain_label or 'Correlation window'}</strong></div>",
        unsafe_allow_html=True,
    )

    # Sort events by timestamp
    events = sorted(threat_chain, key=lambda e: e.get("timestamp", ""))
    n = len(events)

    # Build scatter series data — x = index, y = fixed row, tooltip shows detail
    scatter_data = []
    label_data = []
    for i, ev in enumerate(events):
        etype = _event_type(ev)
        colour = TYPE_COLOUR.get(etype, GHOST)
        icon = TYPE_ICON.get(etype, "•")
        label = _short_label(ev)
        ts = ev.get("timestamp", "")[:19].replace("T", " ")

        scatter_data.append({
            "value": [i, 0],
            "itemStyle": {"color": colour},
            "name": f"{icon} {label}",
            "tooltip_extra": ts,
        })
        label_data.append(f"{icon}\n{label}")

    # Mark lines connecting consecutive events
    mark_lines = []
    for i in range(n - 1):
        c1 = TYPE_COLOUR.get(_event_type(events[i]), GHOST)
        c2 = TYPE_COLOUR.get(_event_type(events[i + 1]), GHOST)
        mark_lines.append([
            {"coord": [i, 0], "lineStyle": {"color": c1, "width": 2}},
            {"coord": [i + 1, 0]},
        ])

    option = {
        "backgroundColor": "#0F1419",
        "tooltip": {
            "trigger": "item",
            "formatter": "{b}",
            "backgroundColor": "#1E2430",
            "textStyle": {"color": "#E8EDF3"},
        },
        "grid": {"left": "5%", "right": "5%", "top": "30%", "bottom": "25%"},
        "xAxis": {
            "type": "value",
            "min": -0.5,
            "max": n - 0.5,
            "axisLabel": {
                "formatter": lambda v: (
                    events[int(v)].get("timestamp", "")[:16].replace("T", " ")
                    if 0 <= int(v) < n else ""
                ),
                "color": GHOST,
                "fontSize": 9,
                "rotate": 25,
            },
            "splitLine": {"show": False},
            "axisLine": {"lineStyle": {"color": GHOST}},
        },
        "yAxis": {
            "type": "value",
            "min": -1,
            "max": 1,
            "axisLabel": {"show": False},
            "axisLine": {"show": False},
            "splitLine": {"show": False},
        },
        "series": [
            {
                "type": "scatter",
                "data": [d["value"] for d in scatter_data],
                "symbolSize": 28,
                "label": {
                    "show": True,
                    "position": "top",
                    "formatter": "{b}",
                    "color": "#E8EDF3",
                    "fontSize": 9,
                    "overflow": "break",
                    "width": 90,
                },
                "markLine": {
                    "silent": True,
                    "symbol": ["none", "arrow"],
                    "data": mark_lines,
                },
            }
        ],
    }

    # Inject name into each point for tooltip
    for i, d in enumerate(scatter_data):
        option["series"][0]["data"][i] = {
            "value": d["value"],
            "name": d["name"],
            "itemStyle": d["itemStyle"],
        }

    st_echarts(option, height="260px", key=f"threat_chain_{alert.get('alert_id', 'x')}")

    # Expandable raw event list
    with st.expander("Raw events in correlation window"):
        for ev in events:
            etype = _event_type(ev)
            icon = TYPE_ICON.get(etype, "•")
            ts = ev.get("timestamp", "")[:19].replace("T", " ")
            col1, col2 = st.columns([1, 4])
            col1.markdown(f"**{icon} {etype.upper()}**")
            col2.caption(
                f"{ts} | {ev.get('mitre_tag') or ev.get('fatf_tag') or ''} | "
                f"src: {ev.get('src_ip', '')} | "
                f"{'₹' + str(ev.get('amount_inr', '')) if ev.get('amount_inr') else 'sev: ' + str(ev.get('severity', ''))}"
            )
