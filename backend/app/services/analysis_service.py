"""Analysis orchestrator.

This is the one place that runs the whole pipeline end to end and assembles the
final `AnalysisResult` dict the API returns. Keeping orchestration here (not in
the API layer) means the entire analysis can be unit-tested without HTTP, and
the API endpoint stays a thin wrapper.
"""
from __future__ import annotations

from ..core.errors import EmptyInputError
from ..core.logging import get_logger
from ..llm.client import LLMClient
from ..llm.explanation import build_explanation, build_gaps, build_strengths
from ..llm.interview import build_interview_prep
from ..llm.recommendations import build_recommendations
from ..ml.embeddings import get_semantic_engine
from ..ml.matching import match_skills
from ..ml.skill_extractor import extract_skills, group_by_category
from ..scoring.scoring_engine import compute_score
from .jd_parser import parse_job_description
from .resume_parser import parse_resume
from .text_cleaning import clean_text

logger = get_logger(__name__)

_PROJECT_KEYS = ("projects",)
_EXPERIENCE_KEYS = ("experience",)


def _role_title(jd_text: str) -> str:
    """Use the first non-empty line of the JD as the role title."""
    for line in jd_text.split("\n"):
        if line.strip():
            return line.strip()[:120]
    return ""


def _section_text(sections: dict, keys) -> str:
    return "\n".join(sections.get(k, "") for k in keys).strip()


def analyze(resume_text: str, jd_text: str) -> dict:
    """Run the full analysis and return the result as a serialisable dict."""
    resume_clean = clean_text(resume_text)
    jd_clean = clean_text(jd_text)

    if len(resume_clean) < 20:
        raise EmptyInputError("The resume text is empty or too short to analyse.")
    if len(jd_clean) < 20:
        raise EmptyInputError("The job description is empty or too short to analyse.")

    resume = parse_resume(resume_clean)
    jd = parse_job_description(jd_clean)
    role_title = _role_title(jd_clean)

    resume_skills = extract_skills(resume_clean)
    engine = get_semantic_engine()

    match = match_skills(resume_skills, jd, engine)

    projects_text = _section_text(resume.sections, _PROJECT_KEYS)
    experience_text = _section_text(resume.sections, _EXPERIENCE_KEYS)

    score = compute_score(
        match, resume_clean, projects_text, experience_text, jd_clean, engine
    )

    recommendations = build_recommendations(match, role_title)
    interview_prep = build_interview_prep(match, role_title)
    strengths = build_strengths(match, score)
    gaps = build_gaps(match)
    explanation = build_explanation(score, match, role_title)

    llm_used = (
        recommendations.get("source") == "llm"
        or interview_prep.get("source") == "llm"
    )

    return {
        "overall_score": round(score.overall, 1),
        "explanation": explanation,
        "score_breakdown": score.to_dict()["components"],
        "skills": {
            "matched": [m.to_dict() for m in match.matched],
            "related": [m.to_dict() for m in match.related],
            "missing": [m.to_dict() for m in match.missing],
            "resume_by_category": group_by_category(resume_skills),
        },
        "resume": {
            "name": resume.name,
            "email": resume.email,
            "phone": resume.phone,
            "links": resume.links,
            "sections_found": list(resume.sections.keys()),
        },
        "job": {
            "role_title": role_title,
            "required_skills": [s.canonical for s in jd.required_skills],
            "preferred_skills": [s.canonical for s in jd.preferred_skills],
            "years_experience": jd.years_experience,
            "education": jd.education,
        },
        "strengths": strengths,
        "gaps": gaps,
        "recommendations": recommendations,
        "interview_prep": interview_prep,
        "meta": {
            "llm_used": llm_used,
            "llm_enabled": LLMClient().is_enabled,
            "embedding_backend": engine.name,
            "warnings": score.warnings,
        },
    }
