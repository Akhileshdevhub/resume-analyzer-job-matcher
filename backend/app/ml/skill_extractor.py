"""Skill extraction + normalisation.

Given free text (a resume or a job description), find every skill from the
taxonomy that it mentions, and report it under its canonical name. This is
deliberately a dictionary / phrase-matching approach rather than a learned
model, because it is:
  * explainable — each result records the exact text that produced it, and
    whether normalisation changed the surface form ("psql" -> "PostgreSQL");
  * deterministic — same input, same output, which makes it unit-testable.

Matching rules that keep precision high:
  * Aliases are tried longest-first, so "machine learning" wins over "ml" and
    "spring boot" wins over "spring". A matched span is consumed so a shorter
    alias can't re-match the same words.
  * Boundary look-arounds stop "ml" matching inside "html" or "c" inside "c++".
  * Short, ambiguous aliases (c, go, r, ml, …) only count in a *list-like*
    context (next to a comma / slash / pipe / bracket / line break), because
    those tokens also occur as ordinary English words.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from .skills_taxonomy import (
    ALIAS_TO_SKILL,
    ALL_ALIASES_LONGEST_FIRST,
    AMBIGUOUS_ALIASES,
    CANONICAL_TO_CATEGORY,
    category_label,
)

# Boundary characters: a match must not be flanked by these, so "ml" can't match
# inside "html" and "c" can't match inside "c++" (the "+" blocks it). We
# deliberately EXCLUDE "." and "-" here so a skill at the end of a sentence
# ("...or TensorFlow.") or before a hyphen ("Java-based") still matches. Internal
# dotted tokens like "node.js" are protected instead by longest-first matching:
# the full "node.js" alias is matched and its span consumed before bare "node"
# is ever tried.
_BOUNDARY_CHARS = "a-z0-9+#"

# Delimiters that signal a *list item* (used only for the ambiguous-alias guard).
# Deliberately excludes plain spaces, hyphens, and the string boundaries, so a
# bare ambiguous word ("go to production") in prose is NOT counted, while a real
# list item ("Python, Go, Java") is.
_STRONG_DELIMS = set(",/|;:()[]•·\n\t")


@dataclass
class ExtractedSkill:
    canonical: str
    category: str
    matched_text: str      # the surface form actually found in the text
    normalized: bool       # True if the surface form differed from the canonical name

    def to_dict(self) -> dict:
        return {
            "skill": self.canonical,
            "category": self.category,
            "category_label": category_label(self.category),
            "matched_text": self.matched_text,
            "normalized": self.normalized,
        }


def _alias_pattern(alias: str) -> re.Pattern:
    """Compile a boundary-aware, case-insensitive pattern for one alias."""
    escaped = re.escape(alias)
    return re.compile(
        rf"(?<![{_BOUNDARY_CHARS}]){escaped}(?![{_BOUNDARY_CHARS}])",
        re.IGNORECASE,
    )


# Pre-compile every alias pattern once (import-time cost, cheap per request).
_ALIAS_PATTERNS: dict[str, re.Pattern] = {a: _alias_pattern(a) for a in ALL_ALIASES_LONGEST_FIRST}


def _is_list_context(text: str, start: int, end: int) -> bool:
    """True if the match at [start, end) is adjacent to a strong delimiter or a
    string boundary on at least one side — i.e., it looks like a list item."""
    before = text[start - 1] if start > 0 else ""          # string boundary: not a list delimiter
    after = text[end] if end < len(text) else ""
    return before in _STRONG_DELIMS or after in _STRONG_DELIMS


def extract_skills(text: str) -> list[ExtractedSkill]:
    """Extract a de-duplicated list of skills from `text`.

    Returns one ExtractedSkill per canonical skill, in first-seen order.
    """
    if not text or not text.strip():
        return []

    lowered = text.lower()
    # Working copy we blank out as we consume matches, so overlapping shorter
    # aliases can't double-count the same span.
    remaining = list(lowered)

    found: dict[str, ExtractedSkill] = {}

    for alias in ALL_ALIASES_LONGEST_FIRST:
        pattern = _ALIAS_PATTERNS[alias]
        current = "".join(remaining)
        for match in pattern.finditer(current):
            start, end = match.start(), match.end()
            # Skip if this span was already consumed by a longer alias.
            if "\x00" in current[start:end]:
                continue
            if alias in AMBIGUOUS_ALIASES and not _is_list_context(current, start, end):
                continue
            skill = ALIAS_TO_SKILL[alias]
            if skill.canonical not in found:
                found[skill.canonical] = ExtractedSkill(
                    canonical=skill.canonical,
                    category=skill.category,
                    matched_text=match.group(0),
                    normalized=(alias != skill.canonical.lower()),
                )
            # Consume this span so shorter aliases skip it.
            for i in range(start, end):
                remaining[i] = "\x00"

    return list(found.values())


def canonical_set(skills: list[ExtractedSkill]) -> set[str]:
    """Just the canonical skill names, for fast set operations in matching."""
    return {s.canonical for s in skills}


def group_by_category(skills: list[ExtractedSkill]) -> dict[str, list[str]]:
    """Group canonical skill names by their category label, for display."""
    grouped: dict[str, list[str]] = {}
    for s in skills:
        grouped.setdefault(category_label(s.category), []).append(s.canonical)
    return grouped
