"""Pydantic schemas for all ingestion and alert models."""

from typing import Optional
from pydantic import BaseModel, Field


class TLSMetadata(BaseModel):
    tls_version: str
    cipher_suite: str
    ja3_hash: Optional[str] = None
    ja4_hash: Optional[str] = None
    pqc_downgrade_detected: bool = False
    session_bytes: int = 0
    dest_asn: Optional[int] = None


class CyberEvent(BaseModel):
    event_id: str
    timestamp: str
    src_ip: str
    dest_ip: str
    mitre_tag: str
    severity: float = Field(ge=0.0, le=10.0)
    tls_metadata: Optional[TLSMetadata] = None


class TransactionEvent(BaseModel):
    event_id: str
    timestamp: str
    src_ip: str
    account_id: str
    dest_account_id: str
    amount_inr: float = Field(gt=0)
    fatf_tag: Optional[str] = None
    branch_id: str


class Alert(BaseModel):
    alert_id: str
    created_at: str
    src_ip: str
    account_id: Optional[str] = None
    anomaly_score: float
    tls_risk_score: float
    shap_values: Optional[dict] = None
    shap_waterfall_png: Optional[str] = None
    llm_report: Optional[str] = None
    llm_source: str = "template"
    threat_chain: list[dict] = []
    is_fraud_ring: bool = False
    ring_members: list[str] = []
    mitre_tags: list[str] = []
    fatf_tags: list[str] = []
