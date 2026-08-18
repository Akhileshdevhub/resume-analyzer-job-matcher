"""API-level tests using FastAPI's TestClient (no server needed)."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_skills_catalog():
    r = client.get("/api/skills")
    assert r.status_code == 200
    body = r.json()
    assert body["count"] > 50
    assert "Programming Languages" in body["skills_by_category"]


def test_analyze_text_happy_path(sample_resume_text, sample_jd_text):
    r = client.post(
        "/api/analyze-text",
        json={"resume_text": sample_resume_text, "job_description": sample_jd_text},
    )
    assert r.status_code == 200
    body = r.json()
    assert 0 <= body["overall_score"] <= 100
    assert len(body["score_breakdown"]) == 6
    matched = {s["skill"] for s in body["skills"]["matched"]}
    assert "Python" in matched
    assert body["meta"]["llm_used"] is False  # no LLM configured in tests


def test_analyze_text_rejects_short_input():
    r = client.post(
        "/api/analyze-text",
        json={"resume_text": "too short", "job_description": "also short"},
    )
    # Pydantic min_length validation -> 422
    assert r.status_code == 422


def test_analyze_pdf_happy_path(resume_pdf_bytes, sample_jd_text):
    r = client.post(
        "/api/analyze",
        files={"resume": ("resume.pdf", resume_pdf_bytes, "application/pdf")},
        data={"job_description": sample_jd_text},
    )
    assert r.status_code == 200
    assert r.json()["overall_score"] >= 0


def test_analyze_pdf_rejects_bad_file(sample_jd_text):
    r = client.post(
        "/api/analyze",
        files={"resume": ("resume.pdf", b"not a pdf", "application/pdf")},
        data={"job_description": sample_jd_text},
    )
    assert r.status_code == 422
    assert r.json()["code"] == "invalid_file"
