# Resume / CV Bullet Points

Three framings of the **same real project**. Pick the set that matches the role.
All are truthful to the implementation — no invented users, accuracy figures, or
deployment scale. Add real numbers only once you measure them.

Project title line (any version):

> **AI Resume Analyzer & Job Matcher** — Python, FastAPI, React/TypeScript,
> scikit-learn · [GitHub] · [Live demo]

## Version A — Technical / software-engineering focus

- Built a full-stack resume-to-job matching web app (FastAPI backend, React +
  TypeScript frontend, Dockerised) with a layered, testable architecture and 38
  passing unit/integration tests.
- Designed an explainable scoring engine that decomposes a 0–100 match score into
  six weighted, individually-explained components instead of an opaque model
  output.
- Implemented a boundary-aware skill extractor over a ~95-skill taxonomy with
  alias normalisation, achieving precise matching (e.g. avoiding false positives
  like "ml" inside "html").
- Exposed a typed REST API (FastAPI + Pydantic) with robust validation, global
  error handling, optional SQLAlchemy persistence, and auto-generated OpenAPI docs.

## Version B — AI / ML focus

- Engineered an explainable NLP pipeline that extracts and normalises skills from
  resumes and job descriptions and matches them via exact, synonym, and semantic
  signals.
- Combined a curated skill-relatedness ontology with cosine-similarity search over
  TF-IDF and transformer sentence embeddings (all-MiniLM-L6-v2), with automatic
  backend selection and per-backend calibration.
- Built a transparent weighted scoring model (six components, documented weights)
  that keeps the match score deterministic and auditable rather than LLM-generated.
- Integrated an optional, provider-agnostic LLM layer (OpenAI/Anthropic) for
  grounded recommendations and interview questions, with deterministic fallbacks to
  prevent hallucination.

## Version C — Product / impact focus

- Built a resume analysis product that tells candidates their fit for a specific
  job and exactly how to improve it — matched skills, gaps, project ideas, and
  likely interview questions — in a clean, single-page dashboard.
- Prioritised explainability as the core differentiator: every score is broken down
  and justified, so users can trust and act on it.
- Shipped an end-to-end experience (PDF upload → analysis → recommendations) with a
  polished UI, graceful error handling, and reproducible Docker deployment.
- Made advanced features optional and gracefully degrading (LLM, transformer
  embeddings, database), so the app runs anywhere with zero configuration.

## Note on honesty

Do not add metrics you haven't measured (accuracy %, user counts, latency,
deployment scale). If you deploy it and gather real numbers, add them — measured
figures are far stronger than invented ones and safe to defend.
