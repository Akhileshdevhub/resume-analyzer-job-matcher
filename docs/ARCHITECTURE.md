# System Architecture

This document explains how the AI Resume Analyzer & Job Matcher is put together,
why each piece exists, and the trade-offs behind the main decisions. It is
written to be read start-to-finish before an interview.

## 1. The problem

A candidate has a resume (a PDF) and a job description (free text). They want an
honest, explainable answer to one question: *how well do I fit this role, and
what should I do about the gaps?* A single number ("74%") is useless if it can't
be defended. So the whole system is built around **explainability**: every score
decomposes into named components, and every component traces back to concrete
evidence (a matched skill, a similarity value, a covered requirement).

## 2. High-level shape

```
                         ┌───────────────────────────┐
   Browser (React/TS)    │  Landing → Upload → JD →   │
                         │  Analysis Dashboard        │
                         └─────────────┬─────────────┘
                                       │  HTTP (JSON + multipart)
                                       ▼
                         ┌───────────────────────────┐
   FastAPI backend       │  /api/analyze  endpoint    │
                         └─────────────┬─────────────┘
                                       ▼
        ┌──────────────────────────────────────────────────────────┐
        │                    Analysis pipeline                       │
        │                                                            │
        │  Resume PDF ──► extract text ──► clean ──► detect sections │
        │                                     │                      │
        │                                     ▼                      │
        │                         skill extraction + normalisation   │
        │                                     │                      │
        │  Job description ──► clean ──► requirement extraction       │
        │     (required vs preferred)  ──► skill extraction + norm.   │
        │                                     │                      │
        │                                     ▼                      │
        │   Matching engine:  exact  +  normalised  +  semantic       │
        │        (TF-IDF and/or transformer embeddings + cosine)      │
        │                                     │                      │
        │                                     ▼                      │
        │   Scoring engine:  weighted, documented, explainable        │
        │                                     │                      │
        │                                     ▼                      │
        │   LLM layer (optional):  recommendations, interview Qs,      │
        │        natural-language explanation  — template fallback     │
        └──────────────────────────────┬───────────────────────────┘
                                        ▼
                         ┌───────────────────────────┐
                         │  AnalysisResult (JSON) +   │
                         │  optional history store    │
                         └───────────────────────────┘
```

The key design principle: **the LLM is a leaf, not the trunk.** The trunk
(extraction → skills → matching → score) is deterministic and testable. The LLM
only decorates the result with natural-language recommendations and interview
questions, and even that has a non-LLM fallback. This is a deliberate choice —
it is what makes the project defensible rather than "I asked GPT to rate a
resume."

## 3. Backend layout

```
backend/app/
  main.py              FastAPI app: CORS, routers, global exception handlers
  api/                 HTTP layer — request parsing, response shaping only
  core/                config (env-driven settings), custom errors, logging
  schemas/             Pydantic request/response models (the API contract)
  services/            orchestration: pdf_extraction, text_cleaning,
                       resume_parser, jd_parser, analysis_service
  ml/                  skills_taxonomy, skill_extractor, embeddings, similarity
  scoring/             weights (documented) + scoring_engine (the formula)
  llm/                 provider-agnostic client + recommendations + interview
  db/                  optional SQLAlchemy models + session (analysis history)
  utils/               file validation helpers
```

Each layer has one job and depends only on the layers "below" it. The `api`
layer never contains business logic; the `services`/`ml`/`scoring` layers never
know about HTTP. This separation is what lets the entire scoring pipeline be
unit-tested without starting a web server (see `tests/`).

## 4. The pipeline, stage by stage

1. **PDF extraction** (`services/pdf_extraction.py`) — `pdfplumber` reads text
   page by page. If a PDF is scanned/image-only there is no text layer, so we
   detect the empty result and raise a clean, user-facing error instead of
   crashing.
2. **Text cleaning** (`services/text_cleaning.py`) — normalise whitespace, fix
   hyphenation across line breaks, strip control characters. Cleaning happens
   before any NLP so downstream stages see consistent input.
3. **Section detection** (`services/resume_parser.py`) — a deterministic
   heading matcher splits the resume into education / experience / projects /
   skills / certifications / achievements. Optional spaCy NER pulls the
   candidate's name and organisations; a regex fallback runs if spaCy is absent.
4. **Skill extraction + normalisation** (`ml/skill_extractor.py`,
   `ml/skills_taxonomy.py`) — a curated taxonomy maps surface forms
   ("Postgres", "postgresql", "psql") to a single canonical skill
   ("PostgreSQL") tagged with a category (language / framework / cloud / …).
   Extraction is dictionary + phrase matching over the cleaned text, so it is
   fully explainable: every extracted skill points at the span that produced it.
5. **JD requirement extraction** (`services/jd_parser.py`) — the JD is split
   into "required" vs "preferred/nice-to-have" regions using cue phrases
   ("required", "must have", "preferred", "bonus", "nice to have"), then skills
   are extracted and normalised the same way. Requirement importance
   (required > preferred) feeds directly into scoring weights.
6. **Matching** (`ml/skill_extractor.py` + `ml/similarity.py`) — three signals:
   *exact* (identical canonical skill), *normalised* (different surface form,
   same canonical skill), and *semantic* (cosine similarity between embeddings
   of resume vs JD text/skills, catching "built neural nets in PyTorch" ≈ "deep
   learning frameworks"). Semantic matches are treated as *related*, never as
   proof of a skill.
7. **Scoring** (`scoring/scoring_engine.py`) — a documented weighted sum of six
   components (see `docs/SCORING.md`). Each component is computed
   deterministically and returned with its weight and contribution so the UI can
   show *why*.
8. **LLM decoration** (`llm/`) — recommendations, interview questions, and a
   plain-English explanation. Uses the configured provider when a key is set;
   otherwise deterministic templates built from the actual matched/missing
   skills. Either way the output is grounded in real pipeline data, which is how
   we avoid hallucinated advice.

## 5. Key technical decisions & trade-offs

- **Deterministic core, LLM leaf.** Testable, explainable, cheap, and works
  offline. Trade-off: template fallbacks are less fluent than an LLM. Accepted,
  because correctness and defensibility matter more than prose polish.
- **TF-IDF baseline + optional transformer embeddings.** TF-IDF always works
  (light, no torch) and is a great "did semantics help?" baseline. MiniLM
  embeddings give real semantic similarity when installed. The `embeddings`
  module auto-selects and falls back. Trade-off: two code paths, but it keeps
  the core image small and makes the TF-IDF-vs-embeddings comparison a real,
  demonstrable thing rather than a slide.
- **Curated skill taxonomy vs pure ML skill tagging.** A hand-built taxonomy is
  explainable and accurate for a known skill universe, and it is honest about
  its limits (unknown skills are simply not matched). Trade-off: it needs
  maintenance and won't recognise skills outside the taxonomy — documented as a
  known limitation.
- **Optional persistence.** History uses SQLAlchemy with SQLite by default so
  the app needs zero database setup to run, and Postgres via `docker-compose`
  for a production-like setup. Trade-off: a little extra code for a feature that
  is off the critical path — kept optional behind a flag.

## 6. Data flow of a single request

`POST /api/analyze` (multipart: `resume` file + `job_description` text)
→ validate file (type, size) → extract → clean → parse resume → parse JD →
extract & normalise skills on both sides → match (exact/normalised/semantic) →
score (6 weighted components) → build strengths/gaps → LLM/template
recommendations + interview prep + explanation → assemble `AnalysisResult` →
(optional) persist → return JSON. The frontend renders the dashboard from that
one JSON object.

## 7. What can go wrong (and how it's handled)

Image-only PDF (no text) → friendly 422 with guidance. Empty resume or JD →
validated and rejected early. LLM key missing / provider error / timeout →
silent fallback to templates, `meta.llm_used=false`. Unknown skills → not
matched, surfaced honestly rather than invented. Oversized upload → rejected
before parsing. Every failure path returns a structured error, never a raw
stack trace.
