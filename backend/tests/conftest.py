"""Shared pytest fixtures and test configuration.

We force the lightweight TF-IDF backend and disable history/LLM so tests are
fast, deterministic, and network-free. These env vars are set before any app
module (and therefore `get_settings`) is imported.
"""
from __future__ import annotations

import io
import os
import pathlib

os.environ.setdefault("SEMANTIC_BACKEND", "tfidf")
os.environ.setdefault("ENABLE_HISTORY", "false")
os.environ.setdefault("LLM_PROVIDER", "")

import pytest  # noqa: E402
from reportlab.lib.pagesizes import A4  # noqa: E402
from reportlab.pdfgen import canvas  # noqa: E402

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
DATA = REPO_ROOT / "data"


@pytest.fixture
def sample_resume_text() -> str:
    return (DATA / "sample_resumes" / "candidate_a_ml.txt").read_text()


@pytest.fixture
def sample_jd_text() -> str:
    return (DATA / "sample_jds" / "ml_engineer.txt").read_text()


@pytest.fixture
def resume_pdf_bytes() -> bytes:
    """A tiny valid PDF with some resume-like text, generated in memory."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    text = c.beginText(40, 780)
    for line in [
        "Test Candidate",
        "test@example.com",
        "SKILLS",
        "Python, SQL, Machine Learning, PyTorch, Docker",
        "EXPERIENCE",
        "Built ML models and REST APIs.",
    ]:
        text.textLine(line)
    c.drawText(text)
    c.save()
    return buf.getvalue()
