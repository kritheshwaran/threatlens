from typing import List

from pydantic import BaseModel

from .scan import ScanHistoryItem


class DashboardSummary(BaseModel):
    total_scans: int
    safe_scans: int
    threats_detected: int  # HIGH RISK + CRITICAL
    scans_today: int
    change_vs_yesterday: float  # fraction, e.g. 0.12 = +12%


class ThreatTrendPoint(BaseModel):
    date: str
    safe: int
    suspicious: int
    malicious: int


class ClassificationBreakdownItem(BaseModel):
    name: str
    value: int


class AnalyticsResponse(BaseModel):
    summary: DashboardSummary
    threat_trend: List[ThreatTrendPoint]
    classification_breakdown: List[ClassificationBreakdownItem]
    recent_scans: List[ScanHistoryItem]