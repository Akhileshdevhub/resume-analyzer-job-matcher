"""Recommendation generation (projects / topics / tools / learning areas).

Grounded in the *actual* match report — specifically the missing and related
skills — so recommendations can never drift into skills the analysis didn't
find. Uses the LLM when configured; otherwise falls back to the deterministic
knowledge base. Either way the output shape is identical, so the API contract
doesn't change with the backend.
"""
from __future__ import annotations

from ..core.errors import LLMError
from ..core.logging import get_logger
from ..ml.matching import MatchReport
from ..ml.skills_taxonomy import CLOUD, TOOL
from . import knowledge
from .client import LLMClient

logger = get_logger(__name__)

_MAX_ITEMS = 5


def _priority_missing(match: MatchReport) -> list:
    """Missing skills, required ones first, then preferred."""
    req = [m for m in match.missing if m.importance == "required"]
    pref = [m for m in match.missing if m.importance == "preferred"]
    return req + pref


def _template_recommendations(match: MatchReport) -> dict:
    missing = _priority_missing(match)
    top = missing[:_MAX_ITEMS]

    projects = [{"skill": m.skill, "idea": knowledge.project_idea(m.skill)} for m in top]
    topics = [m.skill for m in missing[: _MAX_ITEMS + 2]]
    tools = [m.skill for m in missing if m.category in (TOOL, CLOUD)][:_MAX_ITEMS]
    learning = [{"skill": m.skill, "what": knowledge.learning_topic(m.skill)} for m in top]

    return {
        "projects": projects,
        "topics": topics,
        "tools": tools,
        "learning": learning,
        "source": "template",
    }


def _llm_recommendations(match: MatchReport, role_title: str, client: LLMClient) -> dict:
    missing = _priority_missing(match)
    matched = [m.skill for m in match.matched]
    missing_names = [m.skill for m in missing]

    system = (
        "You are a concise technical career mentor. You help a candidate close the "
        "gap between their resume and a specific job. Only reference skills from the "
        "lists provided; do not invent skills, tools, or facts."
    )
    user = (
        f"Role: {role_title or 'the target role'}\n"
        f"Skills the candidate already has: {', '.join(matched) or 'none detected'}\n"
        f"Skills the candidate is missing (most important first): {', '.join(missing_names) or 'none'}\n\n"
        "Return JSON with keys:\n"
        '  "projects": list of {"skill","idea"} — concrete portfolio projects that close the top gaps,\n'
        '  "topics": list of strings — technical topics to study,\n'
        '  "tools": list of strings — specific tools/platforms to learn,\n'
        '  "learning": list of {"skill","what"} — what to focus on for each top gap.\n'
        "Keep each idea to one sentence. At most 5 items per list."
    )
    data = client.generate_json(system, user, max_tokens=900)
    # Validate the shape; if anything essential is missing, treat as failure.
    if not all(k in data for k in ("projects", "topics", "tools", "learning")):
        raise LLMError("LLM recommendation response missing required keys.")
    data["source"] = "llm"
    return data


def build_recommendations(match: MatchReport, role_title: str = "") -> dict:
    """Public entry point: try the LLM, fall back to templates on any problem."""
    client = LLMClient()
    if client.is_enabled:
        try:
            return _llm_recommendations(match, role_title, client)
        except LLMError as exc:
            logger.info("LLM recommendations failed (%s); using templates.", exc)
    return _template_recommendations(match)
