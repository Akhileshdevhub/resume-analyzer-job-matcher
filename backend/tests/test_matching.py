"""Tests for the matching engine (exact / normalised / related)."""
from app.ml.embeddings import TfidfEngine
from app.ml.matching import match_skills
from app.ml.skill_extractor import extract_skills
from app.services.jd_parser import parse_job_description


def _match(resume_text, jd_text):
    resume_skills = extract_skills(resume_text)
    jd = parse_job_description(jd_text)
    return match_skills(resume_skills, jd, TfidfEngine())


def test_exact_matches_detected():
    report = _match(
        "Skills: Python, SQL, PyTorch",
        "Required: Python, SQL, PyTorch.",
    )
    matched = {m.skill for m in report.matched}
    assert {"Python", "SQL", "PyTorch"} <= matched
    assert report.missing == []


def test_related_via_ontology():
    # Resume has PyTorch; JD wants TensorFlow -> related (both DL frameworks).
    report = _match(
        "Skills: Python, PyTorch",
        "Required: Python, TensorFlow.",
    )
    related = {m.skill: m for m in report.related}
    assert "TensorFlow" in related
    assert related["TensorFlow"].via == "ontology"
    assert related["TensorFlow"].evidence == "PyTorch"


def test_missing_skills_reported():
    report = _match(
        "Skills: Python",
        "Required: Python, Kubernetes.",
    )
    missing = {m.skill for m in report.missing}
    assert "Kubernetes" in missing


def test_coverage_counts():
    report = _match(
        "Skills: Python, SQL",
        "Required: Python, SQL, Docker.",
    )
    assert report.required_total == 3
    assert report.required_matched == 2
