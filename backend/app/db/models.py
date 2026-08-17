"""SQLAlchemy models for optional analysis history.

One small table. We store the score and a JSON blob of the full result so a past
analysis can be re-displayed without re-running the pipeline. No resume file or
raw resume text is stored — only the derived result — which keeps sensitive
personal data out of the database by default.
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .session import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    role_title: Mapped[str] = mapped_column(String(160), default="")
    candidate_name: Mapped[str] = mapped_column(String(160), default="")
    overall_score: Mapped[float] = mapped_column(Float, default=0.0)
    embedding_backend: Mapped[str] = mapped_column(String(80), default="")
    result_json: Mapped[str] = mapped_column(Text)  # full AnalysisResult, serialised

    def summary(self) -> dict:
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat(),
            "role_title": self.role_title,
            "candidate_name": self.candidate_name,
            "overall_score": self.overall_score,
            "embedding_backend": self.embedding_backend,
        }
