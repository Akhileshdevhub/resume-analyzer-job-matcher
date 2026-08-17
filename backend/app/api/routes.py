"""HTTP API routes.

This layer is intentionally thin: parse the request, call a service, shape the
response. All real logic lives in services/ml/scoring/llm. Errors raised by those
layers are `AppError` subclasses and are turned into clean JSON by the global
handler in main.py.
"""
from __future__ import annotations

from fastapi import APIRouter, File, Form, UploadFile

from ..core.config import get_settings
from ..core.logging import get_logger
from ..db import repository
from ..ml.skills_taxonomy import CANONICAL_TO_CATEGORY, category_label
from ..schemas.analysis import AnalysisResponse, AnalyzeTextRequest
from ..services.analysis_service import analyze
from ..services.pdf_extraction import extract_text_from_pdf
from ..utils.validation import validate_pdf_upload

router = APIRouter(prefix="/api")
logger = get_logger(__name__)


@router.get("/health")
def health() -> dict:
    settings = get_settings()
    return {
        "status": "ok",
        "llm_enabled": settings.llm_enabled,
        "semantic_backend": settings.semantic_backend,
        "history_enabled": settings.enable_history,
    }


@router.get("/skills")
def skills_catalog() -> dict:
    """Expose the taxonomy so the UI can show what the analyser recognises."""
    by_category: dict[str, list[str]] = {}
    for canonical, category in CANONICAL_TO_CATEGORY.items():
        by_category.setdefault(category_label(category), []).append(canonical)
    for v in by_category.values():
        v.sort()
    return {"count": len(CANONICAL_TO_CATEGORY), "skills_by_category": by_category}


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_resume(
    resume: UploadFile = File(..., description="Resume PDF"),
    job_description: str = Form(..., description="Job description text"),
) -> dict:
    """Analyse an uploaded PDF resume against a pasted job description."""
    data = await resume.read()
    validate_pdf_upload(resume.filename or "", resume.content_type, data)
    resume_text = extract_text_from_pdf(data)

    result = analyze(resume_text, job_description)
    _maybe_save(result)
    return result


@router.post("/analyze-text", response_model=AnalysisResponse)
def analyze_text(body: AnalyzeTextRequest) -> dict:
    """Analyse plain-text resume + JD (no PDF). Handy for testing and demos."""
    result = analyze(body.resume_text, body.job_description)
    _maybe_save(result)
    return result


@router.get("/history")
def history(limit: int = 20) -> dict:
    if not get_settings().enable_history:
        return {"enabled": False, "items": []}
    return {"enabled": True, "items": repository.list_analyses(limit=limit)}


def _maybe_save(result: dict) -> None:
    if get_settings().enable_history:
        repository.save_analysis(result)
