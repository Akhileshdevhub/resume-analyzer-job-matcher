"""Interview preparation: likely topics + questions, grounded in THIS match.

The prompt asked for interview questions tied specifically to the job
requirements, the resume, and the gaps — not generic filler. So we build the
topic list from the skills that actually matter for this pairing:
  * matched required skills — the interviewer will probe what you claim;
  * missing required skills — the interviewer will test your gaps.

The LLM (if enabled) writes tailored questions; otherwise the knowledge base
supplies real per-skill questions plus gap-oriented questions.
"""
from __future__ import annotations

from ..core.errors import LLMError
from ..core.logging import get_logger
from ..ml.matching import MatchReport
from . import knowledge
from .client import LLMClient

logger = get_logger(__name__)

_MAX_TOPICS = 8
_MAX_QUESTIONS = 10


def _topics(match: MatchReport) -> list[str]:
    matched_required = [m.skill for m in match.matched if m.importance == "required"]
    missing_required = [m.skill for m in match.missing if m.importance == "required"]
    # Matched-required first (you must defend these), then gaps.
    ordered = matched_required + missing_required
    # De-dupe, preserve order.
    seen, topics = set(), []
    for s in ordered:
        if s not in seen:
            seen.add(s)
            topics.append(s)
    return topics[:_MAX_TOPICS]


def _template_interview(match: MatchReport) -> dict:
    topics = _topics(match)
    questions: list[dict] = []

    # Questions on the skills the candidate claims (matched required).
    for m in [m for m in match.matched if m.importance == "required"][:4]:
        for q in knowledge.interview_questions_for(m.skill)[:1]:
            questions.append({"question": q, "based_on": m.skill, "type": "skill"})

    # Gap questions on the most important missing skills.
    for m in [m for m in match.missing if m.importance == "required"][:3]:
        questions.append(
            {
                "question": f"Your resume doesn't mention {m.skill}. How would you get up to "
                f"speed on it, and what do you already know about it?",
                "based_on": m.skill,
                "type": "gap",
            }
        )

    # A couple more concrete skill questions to round it out.
    for m in [m for m in match.matched if m.importance == "required"][4:6]:
        for q in knowledge.interview_questions_for(m.skill)[:1]:
            questions.append({"question": q, "based_on": m.skill, "type": "skill"})

    return {"topics": topics, "questions": questions[:_MAX_QUESTIONS], "source": "template"}


def _llm_interview(match: MatchReport, role_title: str, client: LLMClient) -> dict:
    matched_required = [m.skill for m in match.matched if m.importance == "required"]
    missing_required = [m.skill for m in match.missing if m.importance == "required"]

    system = (
        "You are an interviewer preparing questions for a specific candidate and role. "
        "Base every question on the provided skills only. Mix questions on skills the "
        "candidate has with questions probing their gaps."
    )
    user = (
        f"Role: {role_title or 'the target role'}\n"
        f"Candidate's relevant skills: {', '.join(matched_required) or 'none detected'}\n"
        f"Candidate's gaps (required skills they lack): {', '.join(missing_required) or 'none'}\n\n"
        "Return JSON with keys:\n"
        '  "topics": list of strings — the topics to revise for this interview,\n'
        '  "questions": list of {"question","based_on","type"} where type is "skill" or "gap".\n'
        "At most 8 topics and 10 questions. Keep questions specific and answerable."
    )
    data = client.generate_json(system, user, max_tokens=1000)
    if "topics" not in data or "questions" not in data:
        raise LLMError("LLM interview response missing required keys.")
    data["source"] = "llm"
    return data


def build_interview_prep(match: MatchReport, role_title: str = "") -> dict:
    client = LLMClient()
    if client.is_enabled:
        try:
            return _llm_interview(match, role_title, client)
        except LLMError as exc:
            logger.info("LLM interview prep failed (%s); using templates.", exc)
    return _template_interview(match)
