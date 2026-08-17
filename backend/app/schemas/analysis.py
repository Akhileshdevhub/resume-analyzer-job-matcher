"""API request/response models — the typed contract between backend and frontend.

These Pydantic models give FastAPI automatic validation and OpenAPI docs. The
flexible sub-structures (recommendations, interview prep) are typed loosely on
purpose, because their exact shape can differ slightly between the LLM and
template backends; the top-level contract stays stable.
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class AnalyzeTextRequest(BaseModel):
    """Body for /api/analyze-text — analyse without uploading a PDF."""

    resume_text: str = Field(..., min_length=20, description="Plain-text resume.")
    job_description: str = Field(..., min_length=20, description="Job description text.")


class ScoreComponentModel(BaseModel):
    key: str
    label: str
    score: float
    weight: float
    contribution: float
    explanation: str


class SkillModel(BaseModel):
    skill: str
    category: str
    category_label: str
    importance: str | None = None
    status: str | None = None
    evidence: str | None = None
    similarity: float | None = None
    via: str | None = None


class AnalysisResponse(BaseModel):
    overall_score: float
    explanation: str
    score_breakdown: list[ScoreComponentModel]
    skills: dict
    resume: dict
    job: dict
    strengths: list[str]
    gaps: list[str]
    recommendations: dict
    interview_prep: dict
    meta: dict


class ErrorResponse(BaseModel):
    error: str
    code: str
