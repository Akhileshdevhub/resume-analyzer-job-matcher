# Concepts & Design Decisions (Teaching Guide)

This document explains every major technical component: what it does, why it's
there, how it works, what we considered instead, the trade-offs, what can go
wrong, and — for each — **how to explain it in an interview**. Read it top to
bottom to understand the whole project.

Only concepts actually used in this project are covered. Where something is
optional (embeddings, spaCy, LLM), that is stated.

---

## 1. PDF text extraction

**What:** Turn resume PDF bytes into plain text (`services/pdf_extraction.py`,
using `pdfplumber`).

**Why:** Resumes arrive as PDFs; everything downstream needs text.

**How:** `pdfplumber` reads each page's embedded **text layer** and concatenates
it. If the total text is tiny, we assume it's a scanned/image PDF (no text layer)
and raise a clear error.

**Why this approach:** Most resumes are exported from Word / Google Docs / LaTeX
and contain real text, so direct extraction is fast and accurate — no OCR needed.

**Alternatives:** `PyPDF2`/`pypdf` (also text-layer, sometimes messier spacing);
OCR with Tesseract (needed only for scanned PDFs, much heavier and error-prone).

**Trade-offs:** No OCR means scanned resumes aren't supported — a deliberate
simplification, surfaced as a friendly error rather than silent garbage.

**What can go wrong:** Encrypted/corrupt PDFs (caught → error), image-only PDFs
(detected via near-empty output → error), unusual layouts (columns) can jumble
order.

**Interview:** "I use pdfplumber to read the PDF's text layer directly, which is
accurate for normal exported resumes. I explicitly detect image-only PDFs — where
there's no text layer — and return a helpful error instead of feeding garbage
into the pipeline. OCR would be the next step if I needed to support scans."

---

## 2. NLP preprocessing (text cleaning)

**What:** Normalise raw text before any analysis (`services/text_cleaning.py`).

**Why:** PDF text is messy — inconsistent whitespace, words split across lines
with hyphens, bullet glyphs, non-breaking spaces. Consistent input makes every
later stage more reliable.

**How:** Unify newlines, join hyphenated line-breaks, strip zero-width chars,
convert bullets/nbsp to spaces, collapse whitespace. A separate
`normalise_for_matching` produces a lowercased form that keeps tokens like `c++`
and `node.js` intact for skill matching.

**Alternatives:** Doing nothing (worse matching); heavy NLP normalisation
(stemming/lemmatising — unnecessary here and would damage skill tokens).

**Trade-offs:** Rule-based cleaning is simple and predictable but won't fix every
exotic PDF artefact.

**Interview:** "Cleaning is a small, deterministic, side-effect-free step that
runs once up front. Keeping display text and matching text separate matters —
skill matching needs `c++` preserved, but embeddings want natural casing."

---

## 3. Skill extraction & normalisation

**What:** Find skills in text and report them under one canonical name
(`ml/skills_taxonomy.py`, `ml/skill_extractor.py`).

**Why:** "psql", "Postgres", "PostgreSQL" are the same skill. Without
normalisation, matching would miss obvious equivalences and coverage would be
wrong.

**How:** A curated taxonomy maps alias → canonical + category. Extraction scans
text for aliases **longest-first** (so "machine learning" beats "ml"), consuming
matched spans, with boundary look-arounds so "ml" can't match inside "html".
Short ambiguous tokens (`c`, `go`, `r`) only count next to a list delimiter.

**Why this approach:** It's explainable (each match records the surface form and
whether normalisation changed it) and accurate for a known skill universe with
zero training data.

**Alternatives:** A learned NER/skill tagger (needs labelled data, less
predictable, but catches unknown skills); pure fuzzy string matching (noisy).

**Trade-offs:** Needs maintenance and won't recognise skills outside the
taxonomy — an honest, documented limitation.

**What can go wrong:** New skills are invisible; ambiguous abbreviations
(precision handled by the list-context rule); over-broad aliases (kept
conservative).

**Interview:** "I normalise skills through a curated taxonomy — alias to canonical
name plus category. Matching is longest-alias-first with word-boundary rules and
a special case for short ambiguous tokens like Go or C, which I only accept in a
list context. It's fully explainable, which matters more here than catching every
obscure skill."

---

## 4. Job-description analysis (required vs preferred)

**What:** Split a JD into required vs preferred regions and extract skills from
each (`services/jd_parser.py`).

**Why:** Not all requirements are equal — missing a *required* skill should hurt
the score more than missing a *nice-to-have*.

**How:** Walk the lines, switching a "current bucket" on cue phrases ("required",
"must have" vs "preferred", "nice to have", "bonus"). Inline cues like
"Required: Python, SQL" keep their content. A skill that's both counts as
required.

**Alternatives:** Treating all JD keywords equally (loses signal); an LLM to
classify importance (less predictable, unnecessary).

**Trade-offs:** Cue-phrase heuristics can misread unusual JD formats.

**Interview:** "I detect the required vs preferred sections by cue phrases and
carry that importance into scoring — required coverage is weighted 0.35, preferred
only 0.10."

---

## 5. TF-IDF vs embeddings (the semantic engine)

**What:** Represent text as vectors so we can measure similarity
(`ml/embeddings.py`). Two backends behind one interface.

**TF-IDF** (Term Frequency–Inverse Document Frequency): each document becomes a
sparse vector weighting words by how often they appear here vs how rare they are
across documents. Similar wording → similar vectors. **Strength:** lightweight,
no model download, explainable. **Weakness:** it only sees surface words — "built
neural nets in PyTorch" and "deep learning frameworks" share no words, so TF-IDF
sees ~0 similarity.

**Embeddings** (sentence-transformers, `all-MiniLM-L6-v2`): a transformer maps
text to a dense vector that captures **meaning**, so those two phrases land close
even with no shared words. **Strength:** real semantic similarity. **Weakness:**
heavier (pulls in PyTorch), and the model must download once.

**Why both:** TF-IDF always works and is a genuine baseline; embeddings upgrade
quality when available. The engine auto-selects (`SEMANTIC_BACKEND=auto`) and
**calibrates** each backend's raw cosine into a comparable 0–1 range.

**Interview:** "I implemented both TF-IDF and transformer embeddings behind one
interface. TF-IDF is a lexical baseline — great when words overlap, blind when
they don't. Embeddings capture meaning, so related-but-differently-worded
experience is caught. The app auto-selects and falls back, which also let me
directly compare the two."

---

## 6. Cosine similarity

**What:** The metric comparing two vectors (`sklearn.metrics.pairwise` and dot
products).

**How:** Cosine similarity is the cosine of the angle between two vectors:
`cos(θ) = (A·B) / (|A||B|)`. It ranges from -1 to 1 (0 to 1 for our non-negative
vectors). **It measures direction, not magnitude** — so a short and a long
document about the same topic still score as similar, which is exactly what we
want (a resume and a JD differ hugely in length).

**Alternatives:** Euclidean distance (sensitive to length/magnitude — bad here);
dot product on normalised vectors (equivalent to cosine, which is what the
embedding backend uses).

**Interview:** "Cosine similarity compares vector *direction*, ignoring length.
That's the right choice for resume vs JD, which differ a lot in length but can
still be about the same thing. I normalise embedding vectors so cosine is just a
dot product."

---

## 7. The relatedness ontology

**What:** A curated graph of sibling skills (`skills_taxonomy._RELATED_GROUPS`)
— e.g. {PyTorch, TensorFlow, Keras}, {AWS, GCP, Azure}.

**Why:** For "related" detection to work reliably (and offline), and to give a
*human-readable reason* ("both are deep-learning frameworks") instead of just a
cosine number.

**How:** If a required JD skill isn't matched, but a resume skill is in its
sibling group, it's flagged *related* (partial credit). Embedding similarity is a
second, open-ended path to "related".

**Interview:** "I combine a curated skill ontology with embeddings. The ontology
gives reliable, explainable relatedness — PyTorch counts as related to a
TensorFlow requirement — and embeddings catch the open-ended cases the ontology
doesn't list."

---

## 8. Explainable weighted scoring

**What:** Combine six components into a 0–100 score, each returned with its
sub-score, weight, and reason (`scoring/`).

**Why:** The whole point of the project. A defensible score decomposes into named
parts tied to evidence.

**How:** `overall = 100 × Σ(weightᵢ × componentᵢ)`, weights summing to 1 (enforced
at import). Related skills earn partial credit; semantic components are calibrated.

**Alternatives:** Ask an LLM for a number (opaque, unstable, indefensible — the
anti-pattern this project deliberately avoids); a trained regressor (needs
labelled data).

**Interview:** "The score is a transparent weighted sum, not an LLM guess. Every
component has a weight and an explanation, so I can trace an 82 back to which
skills matched and how much semantic context contributed. The weights are a
documented design choice, validated to sum to 1."

---

## 9. LLM structured output (optional layer)

**What:** Use an LLM to generate recommendations, interview questions, and the
explanation — as **structured JSON**, grounded in real data (`llm/`).

**Why:** LLMs write fluent, tailored prose. But we only let them *phrase* things,
never decide the score, and we constrain them to the actual matched/missing
skills.

**How:** A provider-agnostic client (OpenAI or Anthropic via `httpx`) sends a
system prompt ("only use these skills; return JSON") and parses the JSON. Any
failure (no key, timeout, bad JSON) → deterministic template fallback. Every call
is time-boxed.

**Avoiding hallucination:** the prompt contains the exact skill lists and
instructs the model to use only those; the deterministic fallback is always
available; and nothing the LLM returns affects the score.

**Interview:** "The LLM is a leaf, not the trunk. It's optional and swappable
between providers, time-boxed, and always falls back to templates. I feed it only
the real matched and missing skills and ask for JSON, so it can summarise but not
invent, and it never touches the score."

---

## 10. FastAPI (backend framework)

**What:** The web framework serving the API (`app/main.py`, `app/api/`).

**Why:** Async, fast, Pydantic-based validation, and automatic OpenAPI/Swagger
docs — ideal for a typed JSON API. Python keeps the API and the ML pipeline in
one language.

**How:** Routes are a thin layer; Pydantic models define the contract; global
exception handlers turn errors into clean JSON.

**Alternatives:** Flask (simpler, no built-in validation/async/docs); Django
(heavier, more than needed).

**Interview:** "FastAPI gives me typed request/response models, automatic docs,
and async out of the box, and keeps the API in the same language as the ML code.
I kept the route layer thin so the pipeline is testable without HTTP."

---

## 11. React + TypeScript (frontend)

**What:** The single-page UI (`frontend/`).

**Why:** Component model fits a dashboard of independent panels; TypeScript gives
a typed contract mirroring the API, catching mistakes at compile time.

**How:** A small state machine (form → loading → dashboard), a typed `api.ts`
client, and presentational components. The score gauge and bars are pure SVG/CSS
— no chart library — for a clean, intentional look and a light bundle.

**Alternatives:** Plain JS (loses type safety); a big component library (heavier,
more generic-looking).

**Interview:** "React with TypeScript, and the API response is fully typed so the
UI and backend share one contract. I drew the visualisations in SVG rather than
pulling in a chart library, which kept the bundle small and the design
deliberate."

---

## 12. PostgreSQL / SQLAlchemy (optional persistence)

**What:** Optional analysis history (`app/db/`).

**Why:** Demonstrates data modelling and lets you list past analyses. Off the
critical path — analysis works without it.

**How:** SQLAlchemy ORM, SQLite by default (zero setup), PostgreSQL via
docker-compose. Only the derived result is stored — no raw resume text — keeping
personal data out of the DB. Saving is best-effort and never breaks a request.

**Alternatives:** No persistence (loses the feature); a full ORM migration setup
(overkill here).

**Interview:** "History is optional and uses SQLAlchemy — SQLite locally,
Postgres in Docker. I store only the derived result, not the resume, so I'm not
persisting personal data unnecessarily, and a DB failure degrades gracefully."

---

## 13. Docker & docker-compose

**What:** Containerisation and one-command full-stack startup.

**Why:** Reproducible environments; "works on my machine" solved; easy deploy.

**How:** A slim Python image for the backend (multi-arg to optionally bake in the
ML stack), a multi-stage Node→nginx image for the frontend, and a compose file
wiring backend + frontend + Postgres, with the frontend's nginx proxying `/api`.

**Interview:** "The backend image is intentionally light by default with an opt-in
build arg for the heavy ML stack — a real size-vs-capability trade-off. The
frontend is a multi-stage build: Node compiles it, nginx serves the static output
and proxies the API."

---

## 14. Security practices

**What:** Basic production hygiene.

**How:** Secrets via env vars, never committed (`.env` git-ignored,
`.env.example` provided); uploads validated (extension, declared type, size, and
the real `%PDF` magic number) before any parsing; uploaded files are never
executed; only derived results are stored; CORS restricted to configured origins;
the container runs as a non-root user.

**Interview:** "I validate uploads by extension, size, and the actual PDF magic
bytes before touching them, keep secrets in the environment, restrict CORS, run
the container as non-root, and never persist the raw resume — only the analysis
result."

---

## 15. Testing

**What:** 38 pytest tests (`backend/tests/`).

**How:** Unit tests for cleaning, extraction/normalisation, JD parsing, matching,
and scoring (including edge cases — empty input, no required skills, boundary
false positives), plus API tests via FastAPI's `TestClient` (happy paths and
error paths). Tests force the TF-IDF backend and disable the LLM so they're fast,
deterministic, and network-free.

**Interview:** "I test the pipeline layer by layer without needing a server, plus
API tests through the TestClient. The interesting ones are the edge cases — that
'ml' doesn't match inside 'html', that a bad PDF returns a clean error, that a
better-fitting resume always scores higher."

---

## 16. Deployment

Covered in [`DEPLOYMENT.md`](DEPLOYMENT.md): backend as a container, frontend as
static hosting, optional managed Postgres, and a pre-deploy checklist (health
check, CORS origins, `VITE_API_BASE` set at build time, secrets not committed).

**Interview:** "Backend as a container on something like Render, frontend as a
static build on Vercel with the API base baked in at build time, and I make sure
the backend's CORS list includes the exact frontend origin."
