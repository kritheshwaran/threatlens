"""
SQLAlchemy models for persisted scans.

Two tables, deliberately split:
    - Scan       -- the core record + result summary (what History/Dashboard list views need)
    - ScanSignal -- the detailed security signals behind that result (one-to-one with Scan),
                    kept separate so listing scans stays a cheap query that doesn't pull
                    every nested JSON blob along with it.
"""

from datetime import datetime, timezone

from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..database.database import Base


class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    url = Column(String, nullable=False)
    normalized_url = Column(String, nullable=False)

    risk_score = Column(Float, nullable=False)
    classification = Column(String, nullable=False, index=True)
    confidence = Column(Float, nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    user = relationship("User", back_populates="scans")
    signal = relationship(
        "ScanSignal", back_populates="scan", uselist=False, cascade="all, delete-orphan"
    )


class ScanSignal(Base):
    """The full Module 4 security report for one scan, stored as JSON columns."""

    __tablename__ = "scan_signals"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=False, unique=True, index=True)

    reasons = Column(JSON, nullable=False, default=list)
    positive_signals = Column(JSON, nullable=False, default=list)
    negative_signals = Column(JSON, nullable=False, default=list)
    url_analysis = Column(JSON, nullable=False, default=dict)
    domain_analysis = Column(JSON, nullable=False, default=dict)
    dns_analysis = Column(JSON, nullable=False, default=dict)
    ssl_analysis = Column(JSON, nullable=False, default=dict)
    threat_intelligence = Column(JSON, nullable=False, default=dict)
    risk_breakdown = Column(JSON, nullable=False, default=dict)

    scan = relationship("Scan", back_populates="signal")