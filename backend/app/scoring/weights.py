"""Scoring weights — the single source of truth for the formula.

The overall match score is a weighted sum of six components, each in [0, 1].
The weights below sum to 1.0, so the overall score is naturally in [0, 100].

Rationale for the split (this is exactly what you'd defend in an interview):

  * required_coverage (0.35)  — the biggest lever. Missing the skills a JD marks
    as *required* is the strongest negative signal, so it dominates.
  * skill_overlap (0.15)      — breadth: what fraction of ALL named JD skills the
    resume matches exactly. Rewards well-rounded coverage.
  * semantic_similarity (0.15)— whole-document meaning overlap, catching relevant
    experience described in different words than the JD uses.
  * project_relevance (0.15)  — do the candidate's *projects* actually look like
    the work in this JD? Evidence beats keyword bingo.
  * preferred_coverage (0.10) — nice-to-haves matter, but less than requirements.
  * experience_relevance (0.10)— how well prior work experience aligns with the role.

Change the numbers here and the whole system re-balances — nothing else needs to
know the weights. They are kept small and legible on purpose.
"""
from __future__ import annotations

WEIGHTS: dict[str, float] = {
    "required_coverage": 0.35,
    "skill_overlap": 0.20,
    "preferred_coverage": 0.10,
    "semantic_similarity": 0.15,
    "project_relevance": 0.10,
    "experience_relevance": 0.10,
}
# Reliable skill-based signals carry ~two-thirds of the score
# (required + overlap + preferred = 0.65); semantic context carries the other
# third (semantic + project + experience = 0.35). This keeps the score anchored
# to concrete skill evidence while still rewarding relevant, differently-worded
# experience.

# Human-friendly labels for the dashboard.
LABELS: dict[str, str] = {
    "required_coverage": "Required Skill Coverage",
    "skill_overlap": "Overall Skill Overlap",
    "semantic_similarity": "Semantic Similarity",
    "project_relevance": "Project Relevance",
    "preferred_coverage": "Preferred Skill Coverage",
    "experience_relevance": "Experience Relevance",
}

# A skill the candidate only *relates* to semantically (not an exact match)
# earns this fraction of the credit of a full match in coverage calculations.
RELATED_CREDIT = 0.5


def validate_weights() -> None:
    """Fail fast if the weights are ever edited to something that isn't a
    proper distribution. Called at import so a bad edit can't ship silently."""
    total = sum(WEIGHTS.values())
    if abs(total - 1.0) > 1e-6:
        raise ValueError(f"Scoring weights must sum to 1.0, got {total:.4f}")


validate_weights()
