# Deployment Guide

This project ships as two deployables — a FastAPI backend and a static React
frontend — plus an optional PostgreSQL database. Below are three ways to run it,
from easiest to production.

> Note: the Docker images in this repo were authored and their compose file
> validated, but they were **not built inside the environment this project was
> generated in** (no Docker daemon there). Build them yourself with the commands
> below — they use standard base images and should build cleanly.

## 1. Local, no Docker (fastest to iterate)

**Backend**

```bash
cd backend
python -m venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# Optional — transformer embeddings (recommended; needs internet to download the model once):
pip install -r requirements-ml.txt && python -m spacy download en_core_web_sm
uvicorn app.main:app --reload --port 8000
```

**Frontend** (in another terminal)

```bash
cd frontend
npm install
npm run dev            # http://localhost:5173  (proxies /api to :8000)
```

Open http://localhost:5173.

## 2. Local, Docker Compose (full stack + Postgres)

```bash
docker compose up --build
# open http://localhost:8080
```

This starts PostgreSQL, the backend (on :8000), and the nginx-served frontend
(on :8080, proxying /api to the backend). To enable the LLM features, export the
keys before `up`:

```bash
export LLM_PROVIDER=openai LLM_MODEL=gpt-4o-mini LLM_API_KEY=sk-...
docker compose up --build
```

To include transformer embeddings in the backend image, set
`INSTALL_ML: "true"` under `backend.build.args` in `docker-compose.yml` (larger
image, ~1–2 GB).

## 3. Production

A clean split: **backend on a container host**, **frontend on static hosting**.

### Backend — Render / Railway / Fly (Docker)

* Deploy the `backend/` directory using its `Dockerfile`.
* Set environment variables (see `.env.example`): at minimum `CORS_ORIGINS` (your
  frontend's URL), and — if you want history — `DATABASE_URL` for a managed
  Postgres. For LLM features add `LLM_PROVIDER`, `LLM_MODEL`, `LLM_API_KEY`.
* For transformer embeddings, build with `--build-arg INSTALL_ML=true` (or set it
  in the platform's build args). The MiniLM model downloads on first run, so the
  host needs outbound internet to huggingface.co.
* The service listens on port 8000.

### Frontend — Vercel / Netlify (static)

* Build command `npm run build`, output directory `dist`, root `frontend/`.
* Set `VITE_API_BASE` to your deployed backend URL (e.g.
  `https://your-api.onrender.com`).
* Add the frontend's URL to the backend's `CORS_ORIGINS`.

### Pre-deploy checklist

- [ ] Backend `/api/health` returns `{"status":"ok"}`.
- [ ] `CORS_ORIGINS` includes the exact frontend origin (scheme + host + port).
- [ ] `VITE_API_BASE` points at the backend and was set **at build time**.
- [ ] A PDF upload and a text analysis both succeed end-to-end.
- [ ] `.env` is NOT committed (only `.env.example` is).
- [ ] If using history, `DATABASE_URL` is set and reachable.

## Environment variables

See `.env.example` for the full annotated list. The important ones:

| Variable | Purpose | Default |
|---|---|---|
| `CORS_ORIGINS` | Allowed frontend origins (comma-separated) | localhost:5173,3000 |
| `SEMANTIC_BACKEND` | `auto` / `tfidf` / `embeddings` | auto |
| `ENABLE_HISTORY` | Persist analyses | true |
| `DATABASE_URL` | SQLite or Postgres URL | sqlite file |
| `LLM_PROVIDER` | `openai` / `anthropic` / empty | empty (templates) |
| `LLM_API_KEY` | Provider key | empty |
| `MAX_UPLOAD_MB` | Upload size limit | 5 |
