"""
SQLAlchemy engine/session setup. DATABASE_URL comes from Settings
(backend/app/core/config.py), which reads it from the environment --
see .env.example for the PostgreSQL connection string shape.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from ..core.config import settings

connect_args = {}
if settings.database_url.startswith("sqlite"):
    # Only relevant for local/test runs against SQLite.
    connect_args = {"check_same_thread": False}

engine = create_engine(settings.database_url, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency: yields a DB session, always closed after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables. Called once on app startup (no migration tool in this module)."""
    # Import models so they're registered on Base.metadata before create_all.
    from ..models import user, scan  # noqa: F401

    Base.metadata.create_all(bind=engine)