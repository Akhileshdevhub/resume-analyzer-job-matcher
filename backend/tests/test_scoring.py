"""Tests for the scoring engine and weight configuration."""
import pytest

from app.ml.embeddings import TfidfEngine
from app.ml.matching import match_skills
from app.ml.skill_extractor import extract_skills
from app.scoring.scoring_engine import compute_score
from app.scoring.weights import WEIGHTS, validate_weights
from app.services.jd_parser import parse_job_description


def _score(resume_text, jd_text):
    engine = TfidfEngine()
    resume_skills = extract_skills(resume_text)
    jd = parse_job_description(jd_text)
    report = match_skills(resume_skills, jd, engine)
    return compute_score(report, resume_text, resume_text, resume_text, jd_text, engine)


def test_weights_sum_to_one():
    validate_weights()  # raises if not
    assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9


def test_score_in_range():
    res = _score("Python, SQL, PyTorch, Docker", "Required: Python, SQL.")
    assert 0.0 <= res.overall <= 100.0


def test_every_component_present_and_bounded():
    res = _score("Python, SQL", "Required: Python, SQL, Docker.")
    keys = {c.key for c in res.components}
    assert keys == set(WEIGHTS.keys())
    for c in res.components:
        assert 0.0 <= c.score <= 1.0


def test_better_fit_scores_higher():
    strong = _score(
        "Skills: Python, SQL, PyTorch, Machine Learning, REST APIs",
        "Required: Python, SQL, PyTorch, Machine Learning, REST APIs.",
    )
    weak = _score(
        "Skills: Java, Spring Boot",
        "Required: Python, SQL, PyTorch, Machine Learning, REST APIs.",
    )
    assert strong.overall > weak.overall


def test_full_required_coverage_gives_full_component():
    res = _score("Python, SQL, Docker", "Required: Python, SQL, Docker.")
    required = next(c for c in res.components if c.key == "required_coverage")
    assert required.score == pytest.approx(1.0)


def test_no_required_skills_sets_warning():
    # A JD with no recognisable skills -> required coverage defaults + warns.
    res = _score("Python", "We want a passionate teammate who loves coffee.")
    assert any("required" in w.lower() for w in res.warnings)
