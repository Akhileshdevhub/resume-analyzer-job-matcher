"""FastAPI application entry point.

Wires together CORS, the API router, global error handling, and optional DB
init. Run locally with:

    uvicorn app.main:app --reload --port 8000
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .core.config import get_settings
from .core.errors import AppError
from .core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Startup/shutdown hook. Initialise the optional history DB on startup;
    never block startup if the (optional) database is unavailable."""
    if settings.enable_history:
        try:
            from .db.session import init_db

            init_db()
            logger.info("History enabled; database initialised.")
        except Exception as exc:
            logger.warning("Could not initialise history DB: %s", exc)
    yield


app = FastAPI(
    title="AI Resume Analyzer & Job Matcher",
    version="1.0.0",
    description="Explainable resume-to-job matching using NLP, a skill taxonomy, "
    "semantic similarity, and a transparent weighted scoring engine.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """Turn expected application errors into clean JSON (no stack traces)."""
    logger.info("Handled %s: %s", exc.__class__.__name__, exc.message)
    return JSONResponse(status_code=exc.status_code, content={"error": exc.message, "code": exc.code})


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Last-resort handler so an unexpected bug returns JSON, not an HTML 500."""
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"error": "An unexpected error occurred. Please try again.", "code": "internal_error"},
    )


# Routes are included after handlers so everything is registered on the app.
from .api.routes import router  # noqa: E402

app.include_router(router)


@app.get("/")
def root() -> dict:
    return {"name": "AI Resume Analyzer & Job Matcher API", "docs": "/docs", "health": "/api/health"}
