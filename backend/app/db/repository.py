"""Thin data-access helpers for analysis history.

Kept separate from the models so the API layer never writes SQL directly.
Saving is best-effort: a DB error is logged and swallowed so it can't break an
otherwise-successful analysis.
"""
from __future__ import annotations

import json

from ..core.logging import get_logger
from .models import Analysis
from .session import SessionLocal

logger = get_logger(__name__)


def save_analysis(result: dict) -> int | None:
    """Persist an analysis result; return its id, or None if saving failed."""
    try:
        with SessionLocal() as session:
            row = Analysis(
                role_title=result.get("job", {}).get("role_title", "")[:160],
                candidate_name=(result.get("resume", {}).get("name") or "")[:160],
                overall_score=float(result.get("overall_score", 0.0)),
                embedding_backend=result.get("meta", {}).get("embedding_backend", "")[:80],
                result_json=json.dumps(result),
            )
            session.add(row)
            session.commit()
            return row.id
    except Exception as exc:  # persistence must never break the request
        logger.warning("Failed to save analysis history: %s", exc)
        return None


def list_analyses(limit: int = 20) -> list[dict]:
    try:
        with SessionLocal() as session:
            rows = (
                session.query(Analysis)
                .order_by(Analysis.created_at.desc())
                .limit(limit)
                .all()
            )
            return [r.summary() for r in rows]
    except Exception as exc:
        logger.warning("Failed to list analysis history: %s", exc)
        return []
