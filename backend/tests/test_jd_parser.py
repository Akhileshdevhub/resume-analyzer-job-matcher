"""Tests for job-description parsing (required vs preferred split)."""
from app.services.jd_parser import parse_job_description

JD = """Machine Learning Engineer

Required qualifications
- Strong Python skills.
- Experience with PyTorch.
- SQL for data extraction.

Preferred qualifications
- Experience with Docker.
- Familiarity with AWS.
"""


def test_required_and_preferred_are_separated():
    jd = parse_job_description(JD)
    required = {s.canonical for s in jd.required_skills}
    preferred = {s.canonical for s in jd.preferred_skills}

    assert {"Python", "PyTorch", "SQL"} <= required
    assert {"Docker", "AWS"} <= preferred
    # A preferred skill must not also appear in required.
    assert required.isdisjoint(preferred)


def test_years_and_education_detection():
    jd = parse_job_description("Requires 3+ years experience and a Bachelor's degree in CS.")
    assert jd.years_experience == 3
    assert jd.education is not None


def test_skill_that_is_required_wins_over_preferred():
    text = "Required: Python.\nPreferred: Python tooling and Docker."
    jd = parse_job_description(text)
    required = {s.canonical for s in jd.required_skills}
    preferred = {s.canonical for s in jd.preferred_skills}
    assert "Python" in required
    assert "Python" not in preferred
