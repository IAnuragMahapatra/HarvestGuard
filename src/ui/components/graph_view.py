"""Network threat graph. Force-directed echarts showing IPs, accounts and fraud rings."""

import streamlit as st
from streamlit_echarts import st_echarts

CATEGORIES = [
    {"name": "IP Address", "itemStyle": {"color": "#29B6F6"}},
    {"name": "Normal Account", "itemStyle": {"color": "#00E676"}},
    {"name": "Flagged Account", "itemStyle": {"color": "#E53935"}},
    {"name": "Fraud Ring Member", "itemStyle": {"color": "#FFB300"}},
]


def render(graph_data: dict) -> None:
    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])

    if not nodes:
        st.caption("No graph data available.")
        return

    option = {
        "backgroundColor": "#0F1419",
        "tooltip": {
            "trigger": "item",
            "backgroundColor": "#1E2430",
            "textStyle": {"color": "#E8EDF3"},
        },
        "legend": {
            "data": [c["name"] for c in CATEGORIES],
            "textStyle": {"color": "#8892A4"},
            "top": 8,
        },
        "series": [
            {
                "type": "graph",
                "layout": "force",
                "categories": CATEGORIES,
                "data": nodes,
                "edges": edges,
                "roam": True,
                "draggable": True,
                "force": {
                    "repulsion": 120,
                    "edgeLength": [60, 120],
                    "gravity": 0.1,
                },
                "lineStyle": {"color": "#8892A4", "opacity": 0.6, "width": 1.5},
                "emphasis": {
                    "focus": "adjacency",
                    "lineStyle": {"width": 3},
                },
                "label": {
                    "show": True,
                    "color": "#E8EDF3",
                    "fontSize": 9,
                    "position": "right",
                },
            }
        ],
    }

    st_echarts(option, height="360px", key="network_graph")
