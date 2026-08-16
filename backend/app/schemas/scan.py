from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class ScanRequest(BaseModel):
    url: str = Field(..., min_length=1, examples=["https://example.com"])


class Factor(BaseModel):
    label: str
    positive: bool


class WhoisInfo(BaseModel):
    available: bool
    error: Optional[str] = None
    registrar: Optional[str] = None
    creation_date: Optional[str] = None
    expiration_date: Optional[str] = None
    updated_date: Optional[str] = None
    domain_age_days: Optional[int] = None
    days_until_expiry: Optional[int] = None
    status: list[str] = []
    name_servers: list[str] = []


class DomainAnalysis(BaseModel):
    hostname: str
    registrable_domain: str
    subdomain: str
    is_ip: bool
    whois: WhoisInfo


class DNSRecordResult(BaseModel):
    records: list[str]
    error: Optional[str] = None


class DNSAnalysis(BaseModel):
    hostname: str
    records: dict[str, DNSRecordResult]
    resolved: bool


class SSLAnalysis(BaseModel):
    has_ssl: bool
    certificate_valid: Optional[bool] = None
    is_expired: Optional[bool] = None
    is_not_yet_valid: Optional[bool] = None
    not_before: Optional[str] = None
    not_after: Optional[str] = None
    days_until_expiry: Optional[int] = None
    issuer: Optional[str] = None
    issuer_common_name: Optional[str] = None
    subject_common_name: Optional[str] = None
    subject_alt_names: list[str] = []
    protocol_version: Optional[str] = None
    cipher: Optional[str] = None
    error: Optional[str] = None


class UrlAnalysis(BaseModel):
    ml_model: str
    ml_phishing_probability: float
    features: dict
    factors: list[Factor]


class ThreatIntelligence(BaseModel):
    virus_total: dict
    abuseipdb: dict
    openphish: dict
    phishtank: dict
    sources_checked: int
    sources_available: int
    overall: dict


class RiskBreakdown(BaseModel):
    sub_scores: dict
    weights: dict


class ScanResponse(BaseModel):
    id: int
    url: str
    normalized_url: str
    risk_score: float
    classification: Literal["SAFE", "LOW RISK", "MEDIUM RISK", "HIGH RISK", "CRITICAL"]
    confidence: float
    created_at: datetime
    reasons: list[str]
    positive_signals: list[str]
    negative_signals: list[str]
    url_analysis: UrlAnalysis
    domain_analysis: DomainAnalysis
    dns_analysis: DNSAnalysis
    ssl_analysis: SSLAnalysis
    threat_intelligence: ThreatIntelligence
    risk_breakdown: RiskBreakdown


class ScanHistoryItem(BaseModel):
    id: int
    url: str
    normalized_url: str
    risk_score: float
    classification: Literal["SAFE", "LOW RISK", "MEDIUM RISK", "HIGH RISK", "CRITICAL"]
    confidence: float
    created_at: datetime

    model_config = {"from_attributes": True}