"""
Quantum / HNDL risk monitor.

Scores TLS metadata against known harvest-now-decrypt-later indicators.
"""

from typing import Optional

DEPRECATED_CIPHER_SUITES = {
    "TLS_RSA_WITH_RC4_128_MD5",
    "TLS_RSA_WITH_RC4_128_SHA",
    "TLS_RSA_WITH_3DES_EDE_CBC_SHA",
    "TLS_RSA_WITH_AES_128_CBC_SHA",
    "TLS_RSA_WITH_AES_256_CBC_SHA",
    "TLS_RSA_WITH_AES_128_CBC_SHA256",
    "TLS_RSA_WITH_AES_256_CBC_SHA256",
    # RSA key exchange without PFS — classic HNDL target
    "TLS_RSA_WITH_AES_128_GCM_SHA256",
    "TLS_RSA_WITH_AES_256_GCM_SHA384",
    "TLS_RSA_WITH_CHACHA20_POLY1305_SHA256",
}

TRUSTED_ASNS = {
    # Major Indian financial & cloud ASNs
    9498,   # Bharti Airtel
    24560,  # Bharti Airtel Broadband
    17813,  # MTNL Mumbai
    45609,  # Bank of Maharashtra
    15169,  # Google
    16509,  # Amazon
    8075,   # Microsoft
    13335,  # Cloudflare
}

FIFTY_MB = 50 * 1024 * 1024


def score_tls(tls_metadata: Optional[dict]) -> float:
    """Returns a risk score in [0.0, 1.0]. ≥0.5 triggers a Quantum Risk alert."""
    if not tls_metadata:
        return 0.0

    score = 0.0

    tls_version = tls_metadata.get("tls_version", "1.3")
    try:
        version_float = float(tls_version)
        if version_float < 1.3:
            score += 0.3
    except (ValueError, TypeError):
        pass

    cipher = tls_metadata.get("cipher_suite", "")
    if cipher in DEPRECATED_CIPHER_SUITES:
        score += 0.4

    if tls_metadata.get("pqc_downgrade_detected", False):
        score += 0.5

    session_bytes = tls_metadata.get("session_bytes", 0) or 0
    dest_asn = tls_metadata.get("dest_asn")
    if session_bytes > FIFTY_MB and dest_asn not in TRUSTED_ASNS:
        score += 0.3

    return min(score, 1.0)


def explain_tls(tls_metadata: dict) -> dict:
    """Returns which heuristics fired and their contribution."""
    findings = {}

    tls_version = tls_metadata.get("tls_version", "1.3")
    try:
        if float(tls_version) < 1.3:
            findings["tls_version"] = f"TLS {tls_version} (deprecated — not TLS 1.3)"
    except (ValueError, TypeError):
        pass

    cipher = tls_metadata.get("cipher_suite", "")
    if cipher in DEPRECATED_CIPHER_SUITES:
        findings["cipher_suite"] = f"{cipher} (RSA key exchange, no PFS — HNDL target)"

    if tls_metadata.get("pqc_downgrade_detected"):
        findings["pqc_downgrade"] = "PQC downgrade detected — client offered ML-KEM but server fell back to RSA/ECC"

    session_bytes = tls_metadata.get("session_bytes", 0) or 0
    dest_asn = tls_metadata.get("dest_asn")
    if session_bytes > FIFTY_MB and dest_asn not in TRUSTED_ASNS:
        mb = session_bytes / (1024 * 1024)
        findings["volume"] = f"{mb:.0f}MB to untrusted ASN {dest_asn} — matches HNDL exfiltration pattern"

    return findings
