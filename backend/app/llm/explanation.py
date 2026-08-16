"""Natural-language explanation of the result, plus strengths and gaps.

Strengths and gaps are derived deterministically from the match report — they're
facts about the analysis, not opinions, so no LLM is needed. The one-paragraph
overall explanation is templated from the real numbers by default, and can be
upgraded to an LLM phrasing when configured (still fed only real data, so it can
summarise but not invent).
"""
from __future__ import annotations

from ..core.errors import LLMError
from ..core.logging import get_logger
from ..ml.matching import MatchReport
from ..scoring.scoring_engine import ScoreResult
from .client import LLMClient

logger = get_logger(__name__)


def build_strengths(match: MatchReport, score: ScoreResult) -> list[str]:
    strengths: list[str] = []

    matched_required = [m.skill for m in match.matched if m.importance == "required"]
    if matched_required:
        shown = ", ".join(matched_required[:6])
        strengths.append(f"Matches key required skills: {shown}.")

    related = [f"{m.evidence} (for {m.skill})" for m in match.related]
    if related:
        strengths.append("Has closely related experience for: " + ", ".join(related[:4]) + ".")

    # Call out any component the candidate scores well on.
    for c in score.components:
        if c.score >= 0.75 and c.key != "required_coverage":
            strengths.append(c.explanation)

    if not strengths:
        strengths.append("Some overlap with the role, but no standout strengths for these requirements.")
    return strengths


def build_gaps(match: MatchReport) -> list[str]:
    gaps: list[str] = []
    missing_required = [m.skill for m in match.missing if m.importance == "required"]
    missing_preferred = [m.skill for m in match.missing if m.importance == "preferred"]

    if missing_required:
        gaps.append("Missing required skills: " + ", ".join(missing_required) + ".")
    if missing_preferred:
        gaps.append("Missing preferred skills: " + ", ".join(missing_preferred) + ".")
    if not gaps:
        gaps.append("No required or preferred skills are missing — strong coverage.")
    return gaps


def _band(overall: float) -> str:
    if overall >= 75:
        return "a strong match"
    if overall >= 55:
        return "a solid match"
    if overall >= 40:
        return "a partial match"
    return "a weak match"


def _template_explanation(score: ScoreResult, match: MatchReport) -> str:
    matched_required = [m.skill for m in match.matched if m.importance == "required"]
    missing_required = [m.skill for m in match.missing if m.importance == "required"]

    parts = [f"Overall this resume is {_band(score.overall)} for the role "
             f"({score.overall:.0f}/100)."]
    if matched_required:
        parts.append("It covers " + ", ".join(matched_required[:5]) + ".")
    if missing_required:
        parts.append("The biggest gaps are " + ", ".join(missing_required[:4]) + ".")
    # Name the largest and smallest contributing components for transparency.
    ranked = sorted(score.components, key=lambda c: c.contribution, reverse=True)
    parts.append(
        f"The score is driven most by {ranked[0].label.lower()} and held back most "
        f"by {ranked[-1].label.lower()}."
    )
    return " ".join(parts)


def build_explanation(score: ScoreResult, match: MatchReport, role_title: str = "") -> str:
    client = LLMClient()
    if client.is_enabled:
        try:
            matched = [m.skill for m in match.matched if m.importance == "required"]
            missing = [m.skill for m in match.missing if m.importance == "required"]
            system = (
                "You explain a resume-to-job match score in 2-3 plain sentences. "
                "Use only the numbers and skills provided; do not invent anything."
            )
            user = (
                f"Overall score: {score.overall:.0f}/100 for {role_title or 'the role'}.\n"
                f"Matched required skills: {', '.join(matched) or 'none'}.\n"
                f"Missing required skills: {', '.join(missing) or 'none'}.\n"
                f"Component scores: "
                + "; ".join(f"{c.label} {c.score*100:.0f}%" for c in score.components)
                + "."
            )
            return client.generate(system, user, max_tokens=250).strip()
        except LLMError as exc:
            logger.info("LLM explanation failed (%s); using template.", exc)
    return _template_explanation(score, match)
