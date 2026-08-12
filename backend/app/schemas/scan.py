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


class DomainInfo(BaseModel):
    hostname: str
    registrable_domain: str
    subdomain: str
    is_ip: bool
    whois: WhoisInfo


class DNSRecordResult(BaseModel):
    records: list[str]
    error: Optional[str] = None


class DNSInfo(BaseModel):
    hostname: str
    records: dict[str, DNSRecordResult]
    resolved: bool


class SSLInfo(BaseModel):
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


class ScanResponse(BaseModel):
    url: str
    normalized_url: str
    classification: Literal["safe", "suspicious", "malicious"]
    confidence: float
    risk_score: float
    model_name: str
    features: dict
    factors: list[Factor]
    domain_intelligence: DomainInfo
    dns_intelligence: DNSInfo
    ssl_intelligence: SSLInfo