"""The explainable scoring engine.

Takes the structured resume, the structured JD, and the match report, and
produces an overall score PLUS a full per-component breakdown. Every number is
computed here deterministically — no LLM decides the score. The LLM (if enabled)
only *describes* the result later.

Each component is returned as a ScoreComponent carrying its raw score, its
weight, its contribution to the total, and a one-line explanation, so the UI can
render exactly why the score is what it is.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..ml.matching import MatchReport
from .weights import LABELS, RELATED_CREDIT, WEIGHTS


@dataclass
class ScoreComponent:
    key: str
    label: str
    score: float          # 0..1 raw component score
    weight: float         # 0..1 weight
    contribution: float   # weight * score, in 0..1 (×100 = points added to total)
    explanation: str

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "label": self.label,
            "score": round(self.score * 100, 1),          # shown as a percentage
            "weight": round(self.weight * 100, 1),
            "contribution": round(self.contribution * 100, 1),
            "explanation": self.explanation,
        }


@dataclass
class ScoreResult:
    overall: float                        # 0..100
    components: list[ScoreComponent]
    warnings: list[str]

    def to_dict(self) -> dict:
        return {
            "overall": round(self.overall, 1),
            "components": [c.to_dict() for c in self.components],
            "warnings": self.warnings,
        }


def _safe_ratio(numerator: float, denominator: float, default: float) -> float:
    return numerator / denominator if denominator > 0 else default


def _pct(x: float) -> int:
    return round(x * 100)


def compute_score(
    match: MatchReport,
    resume_text: str,
    projects_text: str,
    experience_text: str,
    jd_text: str,
    engine,
) -> ScoreResult:
    """Compute the six components and combine them into an overall score."""
    warnings: list[str] = []

    # ---- 1. Required coverage (matched fully, related counts partially) ----
    if match.required_total == 0:
        required_cov = 1.0
        warnings.append(
            "No required skills were detected in the job description, so required "
            "coverage could not be measured (it defaults to full credit)."
        )
    else:
        required_cov = (
            match.required_matched + RELATED_CREDIT * match.required_related
        ) / match.required_total
    required_expl = (
        f"{match.required_matched}/{match.required_total} required skills matched"
        + (f" (+{match.required_related} related)" if match.required_related else "")
        + "."
    )

    # ---- 2. Preferred coverage ----
    preferred_cov = _safe_ratio(
        match.preferred_matched + RELATED_CREDIT * match.preferred_related,
        match.preferred_total,
        default=1.0,
    )
    preferred_expl = (
        f"{match.preferred_matched}/{match.preferred_total} preferred skills matched"
        + (f" (+{match.preferred_related} related)" if match.preferred_related else "")
        + "."
        if match.preferred_total
        else "No preferred skills listed."
    )

    # ---- 3. Overall skill overlap (exact matches across all JD skills) ----
    skill_overlap = _safe_ratio(match.jd_matched_skills, match.jd_total_skills, default=0.0)
    overlap_expl = (
        f"{match.jd_matched_skills}/{match.jd_total_skills} of all named JD skills "
        f"are present on the resume."
    )

    # Raw cosines are calibrated per backend (engine.calibrate) into an
    # interpretable 0..1 range before they enter the score.

    # ---- 4. Whole-document semantic similarity ----
    semantic = engine.calibrate(engine.similarity(resume_text, jd_text))
    semantic_expl = (
        f"Overall wording of the resume is {_pct(semantic)}% semantically aligned "
        f"with the job description."
    )

    # ---- 5. Project relevance ----
    # Prefer the projects section; if there is none, fall back to the whole
    # resume at reduced credit (we can't point to specific projects).
    if projects_text.strip():
        project_rel = engine.calibrate(engine.similarity(projects_text, jd_text))
        project_expl = f"Listed projects are {_pct(project_rel)}% aligned with the role."
    else:
        project_rel = 0.7 * engine.calibrate(engine.similarity(resume_text, jd_text))
        project_expl = "No dedicated projects section found; estimated from the whole resume."
        warnings.append("No projects section detected; project relevance is an estimate.")

    # ---- 6. Experience relevance ----
    if experience_text.strip():
        experience_rel = engine.calibrate(engine.similarity(experience_text, jd_text))
        experience_expl = f"Work experience is {_pct(experience_rel)}% aligned with the role."
    elif projects_text.strip():
        experience_rel = 0.7 * engine.calibrate(engine.similarity(projects_text, jd_text))
        experience_expl = "No work-experience section found; estimated from projects."
    else:
        experience_rel = 0.5 * engine.calibrate(engine.similarity(resume_text, jd_text))
        experience_expl = "No experience or projects section found; rough estimate."

    raw = {
        "required_coverage": (required_cov, required_expl),
        "skill_overlap": (skill_overlap, overlap_expl),
        "semantic_similarity": (semantic, semantic_expl),
        "project_relevance": (project_rel, project_expl),
        "preferred_coverage": (preferred_cov, preferred_expl),
        "experience_relevance": (experience_rel, experience_expl),
    }

    components: list[ScoreComponent] = []
    overall = 0.0
    for key, weight in WEIGHTS.items():
        score, expl = raw[key]
        score = max(0.0, min(1.0, float(score)))  # clamp defensively
        contribution = weight * score
        overall += contribution
        components.append(
            ScoreComponent(
                key=key,
                label=LABELS[key],
                score=score,
                weight=weight,
                contribution=contribution,
                explanation=expl,
            )
        )

    return ScoreResult(overall=overall * 100.0, components=components, warnings=warnings)
