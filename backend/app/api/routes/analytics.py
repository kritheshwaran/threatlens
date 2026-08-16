"""
Aggregate dashboard/analytics data for the current user, computed from
their persisted scans. Everything is scoped to current_user.id -- one
user never sees another user's stats.

CLASSIFICATION BUCKETING for the trend chart and legacy 3-tier fields:
    SAFE                        -> "safe"
    LOW RISK, MEDIUM RISK       -> "suspicious"
    HIGH RISK, CRITICAL         -> "malicious"
This keeps the existing Module 1 chart components (which expect
{date, safe, suspicious, malicious}) working unchanged against the
Module 4 five-tier classification.
"""

from collections import defaultdict
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...database.database import get_db
from ...models.scan import Scan
from ...models.user import User
from ...schemas.analytics import (
    AnalyticsResponse,
    ClassificationBreakdownItem,
    DashboardSummary,
    ThreatTrendPoint,
)
from ...schemas.scan import ScanHistoryItem
from ..deps import get_current_user

router = APIRouter()

TREND_DAYS = 8

BUCKET_BY_CLASSIFICATION = {
    "SAFE": "safe",
    "LOW RISK": "suspicious",
    "MEDIUM RISK": "suspicious",
    "HIGH RISK": "malicious",
    "CRITICAL": "malicious",
}


@router.get("/", response_model=AnalyticsResponse)
def get_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scans = (
        db.query(Scan)
        .filter(Scan.user_id == current_user.id)
        .order_by(Scan.created_at.desc())
        .all()
    )

    now = datetime.now(timezone.utc)
    today = now.date()
    yesterday = today - timedelta(days=1)

    total_scans = len(scans)
    safe_scans = sum(1 for s in scans if s.classification == "SAFE")
    threats_detected = sum(1 for s in scans if s.classification in ("HIGH RISK", "CRITICAL"))

    def _as_date(scan):
        dt = scan.created_at
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.date()

    scans_today = sum(1 for s in scans if _as_date(s) == today)
    scans_yesterday = sum(1 for s in scans if _as_date(s) == yesterday)
    change_vs_yesterday = (
        round((scans_today - scans_yesterday) / scans_yesterday, 2) if scans_yesterday else 0.0
    )

    summary = DashboardSummary(
        total_scans=total_scans,
        safe_scans=safe_scans,
        threats_detected=threats_detected,
        scans_today=scans_today,
        change_vs_yesterday=change_vs_yesterday,
    )

    # Threat trend: last TREND_DAYS days, bucketed safe/suspicious/malicious per day.
    trend_buckets = defaultdict(lambda: {"safe": 0, "suspicious": 0, "malicious": 0})
    for scan in scans:
        day = _as_date(scan)
        if (today - day).days >= TREND_DAYS or day > today:
            continue
        bucket = BUCKET_BY_CLASSIFICATION.get(scan.classification, "suspicious")
        trend_buckets[day][bucket] += 1

    threat_trend = []
    for offset in range(TREND_DAYS - 1, -1, -1):
        day = today - timedelta(days=offset)
        counts = trend_buckets.get(day, {"safe": 0, "suspicious": 0, "malicious": 0})
        threat_trend.append(
            ThreatTrendPoint(
                date=day.strftime("%b %-d") if hasattr(day, "strftime") else str(day),
                safe=counts["safe"],
                suspicious=counts["suspicious"],
                malicious=counts["malicious"],
            )
        )

    # Classification breakdown (drives the existing pie/donut chart component).
    classification_counts = defaultdict(int)
    for scan in scans:
        classification_counts[scan.classification] += 1
    classification_breakdown = [
        ClassificationBreakdownItem(name=name, value=count)
        for name, count in classification_counts.items()
    ]

    recent_scans = [ScanHistoryItem.model_validate(s) for s in scans[:5]]

    return AnalyticsResponse(
        summary=summary,
        threat_trend=threat_trend,
        classification_breakdown=classification_breakdown,
        recent_scans=recent_scans,
    )