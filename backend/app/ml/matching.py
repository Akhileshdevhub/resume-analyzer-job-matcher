"""Matching engine: compare resume skills against job requirements.

Three signals, in increasing sophistication:

  1. Exact / normalised match — the resume and JD reference the *same canonical
     skill*. Because both sides were already normalised through the taxonomy,
     "Postgres" on the resume and "PostgreSQL" in the JD are the same canonical
     "PostgreSQL", so this single check covers both exact and normalised cases.

  2. Semantic relatedness — for a required/preferred skill the resume does NOT
     list, we ask the semantic engine whether any resume skill is *close in
     meaning* (e.g. resume "PyTorch" vs JD "TensorFlow", or resume "Machine
     Learning" vs JD "Deep Learning"). If the best similarity clears a
     threshold, we call it *related* rather than a full match.

  3. Everything else is a genuine *gap* (missing).

Crucially, a semantic match is treated as "related", never as proof the
candidate has the skill — related skills count for only partial credit in
scoring. This keeps the system honest.
"""
from __future__ import annotations

from dataclasses import dataclass

from .embeddings import EmbeddingEngine, TfidfEngine
from .skill_extractor import ExtractedSkill
from .skills_taxonomy import category_label, related_canonicals

# Above this cosine similarity, an unmatched JD skill is considered "related" to
# something on the resume. Tuned to be conservative so weak links aren't
# oversold. With the TF-IDF fallback, single-skill similarities rarely reach
# this, so related-skill detection is mainly meaningful with embeddings.
RELATED_THRESHOLD = 0.55


@dataclass
class SkillMatch:
    skill: str
    category: str
    importance: str        # "required" | "preferred"
    status: str            # "matched" | "related" | "missing"
    evidence: str = ""     # resume surface form (matched) or nearest resume skill (related)
    similarity: float = 0.0
    via: str = ""          # how a "related" link was found: "ontology" | "semantic"

    def to_dict(self) -> dict:
        return {
            "skill": self.skill,
            "category": self.category,
            "category_label": category_label(self.category),
            "importance": self.importance,
            "status": self.status,
            "evidence": self.evidence,
            "similarity": round(self.similarity, 3),
            "via": self.via,
        }


@dataclass
class MatchReport:
    matched: list[SkillMatch]
    related: list[SkillMatch]
    missing: list[SkillMatch]

    # Coverage counts used by the scoring engine.
    required_total: int
    required_matched: int
    required_related: int
    preferred_total: int
    preferred_matched: int
    preferred_related: int
    jd_total_skills: int
    jd_matched_skills: int


def _targets(jd) -> list[tuple[str, str, str]]:
    """Flatten JD required + preferred skills into (canonical, category, importance).

    A skill that is both required and preferred keeps its 'required' importance
    (jd_parser already removes such duplicates from the preferred list).
    """
    targets: list[tuple[str, str, str]] = []
    seen: set[str] = set()
    for s in jd.required_skills:
        if s.canonical not in seen:
            targets.append((s.canonical, s.category, "required"))
            seen.add(s.canonical)
    for s in jd.preferred_skills:
        if s.canonical not in seen:
            targets.append((s.canonical, s.category, "preferred"))
            seen.add(s.canonical)
    return targets


def match_skills(
    resume_skills: list[ExtractedSkill],
    jd,
    engine: TfidfEngine | EmbeddingEngine,
    related_threshold: float = RELATED_THRESHOLD,
) -> MatchReport:
    resume_names = [s.canonical for s in resume_skills]
    resume_name_set = set(resume_names)
    evidence_of = {s.canonical: s.matched_text for s in resume_skills}

    targets = _targets(jd)

    matched: list[SkillMatch] = []
    unmatched: list[tuple[str, str, str]] = []
    for canonical, category, importance in targets:
        if canonical in resume_name_set:
            matched.append(
                SkillMatch(
                    skill=canonical,
                    category=category,
                    importance=importance,
                    status="matched",
                    evidence=evidence_of.get(canonical, canonical),
                    similarity=1.0,
                )
            )
        else:
            unmatched.append((canonical, category, importance))

    # Relatedness for the unmatched targets. Two independent signals:
    #   (a) the curated ontology — a resume skill in the same sibling group
    #       (always available, and gives a human-readable reason);
    #   (b) the semantic engine — cosine similarity above a threshold
    #       (open-ended, strongest with transformer embeddings).
    # A target is "related" if EITHER fires; otherwise it's a genuine gap.
    related: list[SkillMatch] = []
    missing: list[SkillMatch] = []

    unmatched_names = [c for c, _, _ in unmatched]
    if unmatched_names and resume_names:
        sims = engine.similarity_matrix(resume_names, unmatched_names)  # (resume, unmatched)
    else:
        sims = None

    for j, (canonical, category, importance) in enumerate(unmatched):
        # (a) ontology: is any resume skill a curated sibling of this target?
        siblings = related_canonicals(canonical) & resume_name_set
        # (b) semantic: nearest resume skill by cosine.
        best_sim, best_name = 0.0, ""
        if sims is not None:
            col = sims[:, j]
            best_i = int(col.argmax())
            best_sim = float(col[best_i])
            best_name = resume_names[best_i]

        if siblings:
            evidence = sorted(siblings)[0]
            related.append(
                SkillMatch(canonical, category, importance, "related",
                           evidence=evidence, similarity=max(best_sim, 0.75), via="ontology")
            )
        elif best_sim >= related_threshold:
            related.append(
                SkillMatch(canonical, category, importance, "related",
                           evidence=best_name, similarity=best_sim, via="semantic")
            )
        else:
            missing.append(
                SkillMatch(canonical, category, importance, "missing", "", best_sim)
            )

    # ---- Coverage counts for scoring ----
    def _count(items: list[SkillMatch], importance: str) -> int:
        return sum(1 for m in items if m.importance == importance)

    required_total = sum(1 for _, _, imp in targets if imp == "required")
    preferred_total = sum(1 for _, _, imp in targets if imp == "preferred")

    return MatchReport(
        matched=matched,
        related=related,
        missing=missing,
        required_total=required_total,
        required_matched=_count(matched, "required"),
        required_related=_count(related, "required"),
        preferred_total=preferred_total,
        preferred_matched=_count(matched, "preferred"),
        preferred_related=_count(related, "preferred"),
        jd_total_skills=len(targets),
        jd_matched_skills=len(matched),
    )
