"""SHAP waterfall + LLM SOC report + Quantum risk panel."""

import base64
import streamlit as st

CRIMSON = "#E53935"
BLUE = "#29B6F6"
SLATE = "#1E2430"
GHOST = "#8892A4"


def render(alert: dict) -> None:
    tls_score = alert.get("tls_risk_score", 0)
    shap_png = alert.get("shap_waterfall_png")
    llm_report = alert.get("llm_report", "")
    llm_source = alert.get("llm_source", "template")

    # ── SHAP waterfall ────────────────────────────────────────────────
    st.markdown("#### 📊 Why did this alert fire?")
    if shap_png:
        img_bytes = base64.b64decode(shap_png)
        st.image(img_bytes, use_container_width=True)
    else:
        st.caption("SHAP waterfall not available for this alert.")

    shap_vals = alert.get("shap_values")
    if shap_vals:
        with st.expander("Raw SHAP values"):
            rows = sorted(shap_vals.items(), key=lambda x: -abs(x[1]))
            for feat, val in rows:
                direction = "▲" if val > 0 else "▼"
                colour = CRIMSON if val > 0 else BLUE
                st.markdown(
                    f'<span style="color:{colour}">{direction} {feat}: {val:+.4f}</span>',
                    unsafe_allow_html=True,
                )

    st.markdown("---")

    # ── LLM SOC report ────────────────────────────────────────────────
    source_badge = (
        f'<span style="font-size:0.7rem;color:{GHOST};background:{SLATE};'
        f'padding:2px 7px;border-radius:10px;margin-left:8px">'
        + ("Local AI, data stays on-premises" if llm_source == "llm" else "Template report, LLM unavailable")
        + "</span>"
    )

    st.markdown(
        f'<div style="border:1px solid #29B6F6;border-radius:8px;padding:14px 16px;'
        f'background:{SLATE};margin-bottom:12px">'
        f'<div style="font-size:1rem;font-weight:700;margin-bottom:8px">'
        f'🤖 AI-Generated SOC Report {source_badge}</div>'
        f'<div style="line-height:1.6;color:#E8EDF3">{llm_report or "Report not available."}</div>'
        f"</div>",
        unsafe_allow_html=True,
    )

    # ── Quantum risk panel ────────────────────────────────────────────
    if tls_score >= 0.5:
        tls_meta = alert.get("threat_chain", [])
        quantum_event = next(
            (e for e in (tls_meta if isinstance(tls_meta, list) else []) if e.get("tls_metadata")),
            {},
        )
        tls_data = quantum_event.get("tls_metadata", {}) or {}

        findings = []
        tls_ver = tls_data.get("tls_version", "")
        try:
            if tls_ver and float(tls_ver) < 1.3:
                findings.append(f"TLS {tls_ver} in use (deprecated, not TLS 1.3)")
        except (ValueError, TypeError):
            pass
        cipher = tls_data.get("cipher_suite", "")
        if cipher:
            findings.append(f"Cipher: {cipher} (RSA key exchange, no Perfect Forward Secrecy)")
        if tls_data.get("pqc_downgrade_detected"):
            findings.append("PQC downgrade: client offered ML-KEM but server fell back to RSA/ECC")
        session_mb = (tls_data.get("session_bytes") or 0) / (1024 * 1024)
        dest_asn = tls_data.get("dest_asn")
        if session_mb > 50:
            findings.append(f"{session_mb:.0f}MB to untrusted ASN {dest_asn}, consistent with HNDL exfiltration")

        findings_html = "".join(f"<li>{f}</li>" for f in findings)
        bar_pct = int(tls_score * 100)

        # build entire panel as one string so the border wraps all content
        st.markdown(
            f'<div style="border:1px solid {BLUE}40;border-radius:8px;padding:18px 20px;'
            f'background:rgba(41,182,246,0.04);margin-top:8px">'
            f'<div style="font-family:\'DM Serif Display\', serif; font-size:1.4rem; font-weight:400; color:{BLUE}; margin-bottom:12px; line-height:1.2;">'
            f"🔐 Quantum / HNDL Risk Detected</div>"
            f'<div style="font-size:0.8rem;color:{GHOST};margin-bottom:6px;text-transform:uppercase;letter-spacing:0.05em;">TLS Risk Score: {tls_score:.2f}</div>'
            f'<div style="background:#1C222C;border-radius:4px;height:8px;margin-bottom:16px">'
            f'<div style="background:{BLUE};width:{bar_pct}%;height:100%;border-radius:4px"></div></div>'
            + (f'<ul style="margin:0 0 14px 0;padding-left:18px;font-size:0.9rem;line-height:1.5;">{findings_html}</ul>' if findings else "")
            + f'<div style="font-size:0.82rem;font-style:italic;color:#B0BEC5">'
            f"This session used deprecated encryption and transferred large volumes to an "
            f"unverified ASN, consistent with a Harvest-Now-Decrypt-Later exfiltration pattern. "
            f"Recommend cipher suite audit and ASN allowlist review.</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
