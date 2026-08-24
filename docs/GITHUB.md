# GitHub Repository Metadata

Everything you need to set up the repository presentation.

## Repository name

```
ai-resume-analyzer-job-matcher
```

## One-line description (repo "About")

> Explainable resume-to-job matching using NLP, skill normalisation, semantic
> similarity, and a transparent weighted scoring engine. FastAPI + React.

(Alternative, shorter:) *AI-powered resume analysis and job matching with an
explainable scoring pipeline.*

## Topics / tags

```
nlp  machine-learning  fastapi  react  typescript  python  scikit-learn
resume-parser  semantic-search  embeddings  tf-idf  explainable-ai
job-matching  pdf-parsing  docker
```

## Short project summary (for a portfolio page or pinned description)

An explainable resume-to-job matcher. Upload a resume PDF and a job description and
get a transparent match score — built from skill coverage and semantic similarity,
broken down component by component — plus your gaps, project ideas to close them,
and likely interview questions. The score is deterministic and auditable; an
optional LLM only phrases the recommendations.

## Tech stack (for the README badge line or About)

Python · FastAPI · scikit-learn · (optional) sentence-transformers · React ·
TypeScript · Tailwind CSS · Docker · PostgreSQL/SQLite · pytest

## Features (bullet list)

- Explainable 0–100 score from six weighted, individually-explained components
- Skill extraction + normalisation over a curated ~95-skill taxonomy
- Exact + normalised + semantic matching (relatedness ontology + embeddings)
- Required vs preferred skill weighting
- Grounded recommendations + interview questions (LLM optional, template fallback)
- Clean React/TypeScript dashboard
- Dockerised, tested (38 tests), documented

## Architecture (one paragraph)

A React/TypeScript SPA calls a layered FastAPI backend. The pipeline extracts and
cleans resume text, splits sections, extracts and normalises skills on both sides,
separates required vs preferred JD skills, matches with exact/normalised/semantic
signals, and combines six weighted components into an explainable score. An
optional, provider-agnostic LLM layer phrases recommendations and interview
questions, with deterministic fallbacks.

## Future improvements

Expand/data-drive the taxonomy, learn scoring weights from labelled pairs, add a
learned skill tagger for out-of-taxonomy skills, cache embeddings, support batch
ranking, and export a shareable PDF report.

## Suggested pinned-repo blurb

> Explainable AI resume analyzer & job matcher (FastAPI + React). Transparent,
> component-by-component match scoring — not a black-box number.
