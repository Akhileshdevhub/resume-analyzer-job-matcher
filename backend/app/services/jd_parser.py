"""Job-description parsing.

A JD is free text, but it has structure we can exploit: it almost always
separates hard *requirements* from *preferred / nice-to-have* qualifications
using cue phrases. We split the text into those regions, then run the same skill
extractor on each region. That importance signal (required vs preferred) flows
straight into the scoring weights, so the score reflects that missing a
*required* skill hurts more than missing a *preferred* one.

Everything here is deterministic and explainable — no LLM is involved in
deciding what the job requires.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from ..ml.skill_extractor import ExtractedSkill, extract_skills

# Cue phrases that mark the start of a region. Checked on lowercased lines.
_PREFERRED_CUES = (
    "preferred", "nice to have", "nice-to-have", "nice to haves", "bonus",
    "good to have", "desired", "a plus", "plus points", "pluses",
    "would be a plus", "optional",
)
_REQUIRED_CUES = (
    "required", "requirement", "must have", "must-have", "minimum qualification",
    "basic qualification", "what you need", "what you'll need", "we require",
    "qualifications", "responsibilities", "you will", "you'll",
)

_YEARS_RE = re.compile(r"(\d+)\+?\s*(?:-\s*\d+\s*)?(?:years|yrs)", re.I)
_DEGREE_RE = re.compile(
    r"\b(bachelor'?s?|b\.?tech|b\.?e\.?|b\.?sc|master'?s?|m\.?tech|m\.?sc|phd|ph\.?d)\b",
    re.I,
)


@dataclass
class StructuredJD:
    required_skills: list[ExtractedSkill] = field(default_factory=list)
    preferred_skills: list[ExtractedSkill] = field(default_factory=list)
    all_skills: list[ExtractedSkill] = field(default_factory=list)
    years_experience: int | None = None
    education: str | None = None
    raw_text: str = ""

    def to_dict(self) -> dict:
        return {
            "required_skills": [s.to_dict() for s in self.required_skills],
            "preferred_skills": [s.to_dict() for s in self.preferred_skills],
            "years_experience": self.years_experience,
            "education": self.education,
        }


def _looks_like_cue_line(line: str, cues: tuple[str, ...]) -> bool:
    """True if a (reasonably short) line contains one of the cue phrases."""
    s = line.strip().lower()
    if not s or len(s) > 60:
        return False
    return any(cue in s for cue in cues)


def _split_regions(text: str) -> tuple[str, str]:
    """Split the JD text into (required_region, preferred_region).

    We walk the lines keeping a 'current bucket'. Preferred cues are checked
    before required cues so a line like "Preferred qualifications" wins even
    though it contains the word "qualifications".
    """
    required_lines: list[str] = []
    preferred_lines: list[str] = []
    bucket = "required"  # text before any cue is treated as a hard requirement

    for line in text.split("\n"):
        # A cue switches the current bucket. We still keep the line's own content
        # in the new bucket, so an INLINE cue like "Required: Python, SQL" doesn't
        # lose its skills (the cue word itself isn't a skill, so it's harmless).
        if _looks_like_cue_line(line, _PREFERRED_CUES):
            bucket = "preferred"
            preferred_lines.append(line)
            continue
        if _looks_like_cue_line(line, _REQUIRED_CUES):
            bucket = "required"
            required_lines.append(line)
            continue
        (required_lines if bucket == "required" else preferred_lines).append(line)

    return "\n".join(required_lines), "\n".join(preferred_lines)


def parse_job_description(text: str) -> StructuredJD:
    required_region, preferred_region = _split_regions(text)

    required = extract_skills(required_region)
    preferred = extract_skills(preferred_region)

    # A skill that shows up as both required and preferred counts as required.
    required_names = {s.canonical for s in required}
    preferred = [s for s in preferred if s.canonical not in required_names]

    all_skills = extract_skills(text)

    years_match = _YEARS_RE.search(text)
    degree_match = _DEGREE_RE.search(text)

    return StructuredJD(
        required_skills=required,
        preferred_skills=preferred,
        all_skills=all_skills,
        years_experience=int(years_match.group(1)) if years_match else None,
        education=degree_match.group(0) if degree_match else None,
        raw_text=text,
    )
