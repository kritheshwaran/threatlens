"""Persistence helpers for scans -- keeps the route handlers thin."""

from sqlalchemy.orm import Session

from ..models.scan import Scan, ScanSignal


def save_scan(db: Session, user_id: int, report: dict) -> Scan:
    """Persist a Module 4 security report (as returned by
    generate_security_report()) as a Scan + ScanSignal row pair."""
    scan = Scan(
        user_id=user_id,
        url=report["url"],
        normalized_url=report["normalized_url"],
        risk_score=report["risk_score"],
        classification=report["classification"],
        confidence=report["confidence"],
    )
    db.add(scan)
    db.flush()  # assigns scan.id without committing yet

    signal = ScanSignal(
        scan_id=scan.id,
        reasons=report["reasons"],
        positive_signals=report["positive_signals"],
        negative_signals=report["negative_signals"],
        url_analysis=report["url_analysis"],
        domain_analysis=report["domain_analysis"],
        dns_analysis=report["dns_analysis"],
        ssl_analysis=report["ssl_analysis"],
        threat_intelligence=report["threat_intelligence"],
        risk_breakdown=report["risk_breakdown"],
    )
    db.add(signal)
    db.commit()
    db.refresh(scan)
    db.refresh(signal)
    scan.signal = signal
    return scan


def scan_to_response_dict(scan: Scan) -> dict:
    """Flatten a Scan (+ its ScanSignal) back into the ScanResponse shape."""
    signal = scan.signal
    return {
        "id": scan.id,
        "url": scan.url,
        "normalized_url": scan.normalized_url,
        "risk_score": scan.risk_score,
        "classification": scan.classification,
        "confidence": scan.confidence,
        "created_at": scan.created_at,
        "reasons": signal.reasons,
        "positive_signals": signal.positive_signals,
        "negative_signals": signal.negative_signals,
        "url_analysis": signal.url_analysis,
        "domain_analysis": signal.domain_analysis,
        "dns_analysis": signal.dns_analysis,
        "ssl_analysis": signal.ssl_analysis,
        "threat_intelligence": signal.threat_intelligence,
        "risk_breakdown": signal.risk_breakdown,
    }


def list_user_scans(db: Session, user_id: int, limit: int = 100):
    return (
        db.query(Scan)
        .filter(Scan.user_id == user_id)
        .order_by(Scan.created_at.desc())
        .limit(limit)
        .all()
    )


def get_user_scan(db: Session, user_id: int, scan_id: int):
    return (
        db.query(Scan)
        .filter(Scan.id == scan_id, Scan.user_id == user_id)
        .first()
    )