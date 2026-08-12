"""Resume parsing: raw text -> structured sections + contact info.

This is deterministic and rule-based on purpose. Resumes follow strong
conventions (a "SKILLS" heading, an "EXPERIENCE" heading, contact details at the
top), so a well-chosen set of rules is accurate, fast, and — crucially —
*explainable*: we can point at exactly which line produced which section.

Named-entity recognition (spaCy) is used only as an optional enhancement for the
candidate's name and organisations. If spaCy isn't installed, a regex/heuristic
fallback runs and the pipeline is unaffected.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from ..core.logging import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Section headings: surface variations -> canonical section name.
# Matching is done on a lowercased, stripped line, so keys are lowercase.
# ---------------------------------------------------------------------------
_HEADING_ALIASES: dict[str, str] = {
    "education": "education",
    "academic background": "education",
    "academics": "education",
    "experience": "experience",
    "work experience": "experience",
    "professional experience": "experience",
    "employment": "experience",
    "internships": "experience",
    "internship experience": "experience",
    "projects": "projects",
    "personal projects": "projects",
    "academic projects": "projects",
    "key projects": "projects",
    "skills": "skills",
    "technical skills": "skills",
    "skills & abilities": "skills",
    "core competencies": "skills",
    "technologies": "skills",
    "certifications": "certifications",
    "certificates": "certifications",
    "licenses & certifications": "certifications",
    "achievements": "achievements",
    "awards": "achievements",
    "honors": "achievements",
    "awards & achievements": "achievements",
    "positions of responsibility": "achievements",
    "summary": "summary",
    "objective": "summary",
    "profile": "summary",
    "about": "summary",
}

_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
_PHONE_RE = re.compile(r"(\+?\d[\d\-\s()]{7,}\d)")
_URL_RE = re.compile(r"(https?://[^\s]+|(?:www\.|linkedin\.com|github\.com)[^\s]+)", re.I)


@dataclass
class StructuredResume:
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    links: list[str] = field(default_factory=list)
    sections: dict[str, str] = field(default_factory=dict)
    raw_text: str = ""

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "links": self.links,
            "sections": self.sections,
        }


def _match_heading(line: str) -> str | None:
    """Return the canonical section name if `line` is a section heading.

    A heading is short, contains no sentence punctuation, and matches (or starts
    with) one of the known aliases. Requiring shortness avoids treating a normal
    sentence that happens to contain "experience" as a heading.
    """
    stripped = line.strip().rstrip(":").lower()
    if not stripped or len(stripped) > 40:
        return None
    if stripped in _HEADING_ALIASES:
        return _HEADING_ALIASES[stripped]
    # Allow "technical skills:" style headings with trailing words removed.
    for alias, canonical in _HEADING_ALIASES.items():
        if stripped == alias or stripped.startswith(alias + " "):
            return canonical
    return None


def _extract_contact(text: str) -> tuple[str | None, str | None, list[str]]:
    email_match = _EMAIL_RE.search(text)
    phone_match = _PHONE_RE.search(text)
    links = list(dict.fromkeys(_URL_RE.findall(text)))  # de-duped, order-kept
    email = email_match.group(0) if email_match else None
    phone = phone_match.group(0).strip() if phone_match else None
    return email, phone, links


def _guess_name(lines: list[str], email: str | None) -> str | None:
    """Heuristic name guess: the first short, title-cased line near the top that
    is not contact info. Used when spaCy NER is unavailable or finds nothing."""
    for line in lines[:6]:
        s = line.strip()
        if not s or "@" in s or _URL_RE.search(s) or any(c.isdigit() for c in s):
            continue
        words = s.split()
        if 1 < len(words) <= 4 and all(w[0].isupper() for w in words if w[:1].isalpha()):
            return s
    # Fall back to the local part of the email address.
    if email:
        return email.split("@")[0].replace(".", " ").replace("_", " ").title()
    return None


def _spacy_name(text: str) -> str | None:
    """Try spaCy NER for a PERSON entity in the first few lines. Optional."""
    try:
        import spacy  # noqa: local import so spaCy stays optional
    except Exception:
        return None
    try:
        nlp = _get_spacy()
        if nlp is None:
            return None
        doc = nlp("\n".join(text.splitlines()[:5]))
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                return ent.text.strip()
    except Exception as exc:
        logger.debug("spaCy name extraction skipped: %s", exc)
    return None


_SPACY_NLP = None


def _get_spacy():
    """Load and cache the small English spaCy model, if available."""
    global _SPACY_NLP
    if _SPACY_NLP is not None:
        return _SPACY_NLP
    try:
        import spacy

        _SPACY_NLP = spacy.load("en_core_web_sm")
    except Exception:
        _SPACY_NLP = None
    return _SPACY_NLP


def parse_resume(text: str) -> StructuredResume:
    """Parse cleaned resume text into a StructuredResume.

    Everything above the first recognised heading is treated as the header
    block (name + contact). Lines under each heading accumulate into that
    section until the next heading appears.
    """
    lines = text.split("\n")
    email, phone, links = _extract_contact(text)

    sections: dict[str, list[str]] = {}
    current = "header"
    sections[current] = []

    for line in lines:
        heading = _match_heading(line)
        if heading:
            current = heading
            sections.setdefault(current, [])
            continue
        sections.setdefault(current, []).append(line)

    header_lines = sections.pop("header", [])
    name = _spacy_name(text) or _guess_name(header_lines or lines, email)

    # Join each section's lines back into text, dropping empties.
    joined = {
        key: "\n".join(l for l in value).strip()
        for key, value in sections.items()
        if "\n".join(value).strip()
    }

    return StructuredResume(
        name=name,
        email=email,
        phone=phone,
        links=links,
        sections=joined,
        raw_text=text,
    )
