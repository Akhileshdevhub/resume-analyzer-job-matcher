# Scoring Methodology

The overall match score is **not** an LLM guessing a number. It is a transparent,
weighted combination of six components, each computed deterministically and each
returned with its own sub-score and explanation. This document is the reference
for exactly how the number is produced.

## The formula

```
overall = 100 × Σ ( weightᵢ × componentᵢ )      where every componentᵢ ∈ [0, 1]
```

| Component | Weight | What it measures |
|---|---|---|
| Required Skill Coverage | 0.35 | Fraction of the JD's **required** skills the resume matches. |
| Overall Skill Overlap | 0.20 | Fraction of **all** named JD skills present on the resume (exact). |
| Preferred Skill Coverage | 0.10 | Fraction of the JD's **preferred / nice-to-have** skills matched. |
| Semantic Similarity | 0.15 | Whole-document meaning overlap (resume vs JD). |
| Project Relevance | 0.10 | How closely the candidate's projects resemble the role. |
| Experience Relevance | 0.10 | How closely prior work experience resembles the role. |

The weights sum to **1.0** and are enforced at import (`weights.validate_weights`).
Skill-based signals (required + overlap + preferred = **0.65**) intentionally
outweigh the semantic signals (**0.35**): the score stays anchored to concrete
skill evidence, while semantics reward relevant experience described in different
words than the JD uses.

## How each component is computed

**Required / Preferred coverage.** A skill can be *matched* (exact/normalised —
same canonical skill on both sides) or *related* (a curated sibling skill or a
high semantic similarity — e.g. resume *PyTorch* for JD *TensorFlow*). A full
match earns 1.0; a related-only skill earns partial credit (`RELATED_CREDIT =
0.5`). So:

```
required_coverage = (required_matched + 0.5 × required_related) / required_total
```

**Overall skill overlap.** `jd_matched_skills / jd_total_skills`, counting exact
matches only — a breadth measure across every skill named in the JD.

**Semantic similarity / Project / Experience relevance.** Cosine similarity from
the semantic engine (TF-IDF baseline, or transformer embeddings when installed),
then **calibrated** into an interpretable 0–1 range. Raw cosine between two
different document types (a resume and a JD) is small even when they're clearly
related, and the useful band differs per backend, so each engine rescales its own
observed band (`TfidfEngine`: [0.0, 0.35] → [0, 1]; `EmbeddingEngine`: [0.20,
0.70] → [0, 1]). Project and experience relevance compare the *projects* and
*experience* sections specifically; if a section is missing, the component falls
back to a reduced-credit estimate and a warning is attached.

## Why it's explainable

Every component returns `{score, weight, contribution, explanation}`. The
dashboard shows the overall number and, directly beneath it, the six
contributions that produced it plus a sentence each (e.g. *"6/8 required skills
matched (+2 related)."*). Nothing about the score is a black box: you can always
trace an 82 back to which skills were matched, which were only related, and how
much semantic context contributed.

## Honest limitations

* Project/experience relevance are semantic by nature and are strongest with the
  transformer-embedding backend. Under the lightweight TF-IDF fallback they read
  low when a project describes specifics (e.g. "MNIST digit classifier") that
  don't lexically overlap the JD — the score stays correctly *ordered*, just
  compressed. The active backend is reported in the result's `meta`.
* Calibration bands are chosen from observed values, not learned from a labelled
  dataset — they're a reasonable heuristic, not a trained calibrator.
* A skill outside the taxonomy is invisible to coverage. Coverage therefore
  measures *recognised* skills, which is why it's paired with semantic signals.
