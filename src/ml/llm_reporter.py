"""
Local LLM SOC reporter. Wraps llama.cpp with an 8-second timeout.
Falls back to a deterministic template when LLM is unavailable or slow.
"""

import concurrent.futures
import logging
import os
from pathlib import Path

logger = logging.getLogger("llm_reporter")

_llm = None
_executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)


def load_llm(model_path: str | None = None) -> None:
    global _llm
    path = model_path or os.getenv("LLM_MODEL_PATH", "models/phi-3-mini-q4.gguf")
    if not Path(path).exists():
        logger.info("LLM model not found at %s, using template mode", path)
        return
    try:
        from llama_cpp import Llama
        _llm = Llama(
            model_path=str(path),
            n_ctx=2048,
            n_threads=4,
            verbose=False,
        )
        logger.info("LLM loaded from %s", path)
    except ImportError:
        logger.info("llama-cpp-python not installed, using template mode")
    except Exception as exc:
        logger.warning("LLM load failed: %s, using template mode", exc)


def generate(alert: dict, shap_top3: dict) -> tuple[str, str]:
    """
    Returns (report_text, source) where source is "llm" or "template".

    8-second hard timeout. Falls back to template if LLM does not respond.
    """
    if _llm is None:
        return _template_report(alert, shap_top3), "template"

    try:
        future = _executor.submit(_call_llm, alert, shap_top3)
        text = future.result(timeout=8)
        return text, "llm"
    except concurrent.futures.TimeoutError:
        logger.warning("LLM timed out after 8s, serving template report")
        return _template_report(alert, shap_top3), "template"
    except Exception as exc:
        logger.warning("LLM error: %s, serving template report", exc)
        return _template_report(alert, shap_top3), "template"


def _call_llm(alert: dict, shap_top3: dict) -> str:
    prompt = _build_prompt(alert, shap_top3)
    output = _llm(
        prompt,
        max_tokens=256,
        temperature=0.2,
        stop=["</report>", "\n\n\n"],
    )
    return output["choices"][0]["text"].strip()


def _build_prompt(alert: dict, shap_top3: dict) -> str:
    mitre = ", ".join(alert.get("mitre_tags", [])) or "unknown"
    fatf = ", ".join(alert.get("fatf_tags", [])) or "none"
    score = alert.get("anomaly_score", 0)
    account = alert.get("account_id", "unknown")
    src_ip = alert.get("src_ip", "unknown")
    tls_score = alert.get("tls_risk_score", 0)

    top_features = "\n".join(
        f"  - {k}: {v:+.3f}" for k, v in sorted(shap_top3.items(), key=lambda x: -abs(x[1]))[:3]
    )

    return f"""You are a banking SOC analyst. Write a concise 3-5 sentence incident report.

Alert data:
- Source IP: {src_ip}
- Account: {account}
- Anomaly score: {score:.2f} (threshold 0.75)
- MITRE ATT&CK tags: {mitre}
- FATF Typology tags: {fatf}
- Quantum/TLS risk score: {tls_score:.2f}
- Top SHAP drivers:
{top_features}

<report>"""


def _template_report(alert: dict, shap_top3: dict) -> str:
    mitre = ", ".join(alert.get("mitre_tags", [])) or "unknown technique"
    fatf = ", ".join(alert.get("fatf_tags", [])) or "no FATF tag"
    score = alert.get("anomaly_score", 0)
    account = alert.get("account_id", "unknown")
    src_ip = alert.get("src_ip", "unknown")
    tls_score = alert.get("tls_risk_score", 0)

    top = sorted(shap_top3.items(), key=lambda x: -abs(x[1]))[:3]
    top_str = ", ".join(f"{k} ({v:+.3f})" for k, v in top)

    report = (
        f"CRITICAL: IP {src_ip} executed {mitre} before successful authentication. "
        f"Account {account} subsequently initiated high-velocity transfers consistent with "
        f"{fatf}, a known financial crime typology. "
        f"Composite anomaly score: {score:.2f}. "
        f"Primary SHAP drivers: {top_str}. "
    )

    if tls_score >= 0.5:
        report += (
            f"Additionally, a TLS session from this IP scored {tls_score:.2f} on the "
            f"quantum risk scale, consistent with a Harvest-Now-Decrypt-Later exfiltration pattern. "
            f"Recommend immediate account freeze, SOC escalation, and cipher suite audit."
        )
    else:
        report += "Recommend immediate account freeze and SOC escalation."

    return report
