"""Database session + engine (optional persistence).

History is an optional feature (ENABLE_HISTORY). SQLite is the zero-setup
default so the app runs with no database to install; the same code talks to
PostgreSQL when DATABASE_URL points at one (see docker-compose). Persistence is
deliberately off the critical path — if the DB is unavailable, analysis still
works; only history saving is skipped.
"""
from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from ..core.config import get_settings


class Base(DeclarativeBase):
    pass


_settings = get_settings()

# check_same_thread is a SQLite-only flag; harmless to pass conditionally.
_connect_args = {"check_same_thread": False} if _settings.database_url.startswith("sqlite") else {}

engine = create_engine(_settings.database_url, connect_args=_connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def init_db() -> None:
    """Create tables if they don't exist. Called once on startup."""
    from . import models  # noqa: F401 — ensure models are registered on Base

    Base.metadata.create_all(bind=engine)
