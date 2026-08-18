"""Tests for skill extraction and normalisation."""
from app.ml.skill_extractor import canonical_set, extract_skills


def _names(text):
    return canonical_set(extract_skills(text))


def test_exact_and_normalised_forms_map_to_canonical():
    assert "PostgreSQL" in _names("experience with postgres and psql")
    assert "JavaScript" in _names("strong JS skills")
    assert "Machine Learning" in _names("ML and data pipelines")
    assert "AWS" in _names("deployed on Amazon Web Services")


def test_special_char_tokens():
    names = _names("C++, C# and Node.js")
    assert {"C++", "C#", "Node.js"} <= names


def test_boundaries_prevent_substring_false_positives():
    # "ml" must not match inside "html"; "c" must not match inside "c++" as C.
    assert "Machine Learning" not in _names("I write html and css")


def test_ambiguous_tokens_need_list_context():
    # Bare "go" in prose should NOT be detected...
    assert "Go" not in _names("I will go to production tomorrow")
    # ...but in a skills list it should.
    assert "Go" in _names("Languages: Python, Go, Java")


def test_trailing_punctuation_still_matches():
    assert "TensorFlow" in _names("Frameworks: PyTorch or TensorFlow.")


def test_longest_alias_wins():
    # "spring boot" should map to Spring Boot, not just "spring".
    assert "Spring Boot" in _names("built services in Spring Boot")


def test_empty_input_returns_empty():
    assert extract_skills("") == []
    assert extract_skills("   ") == []


def test_normalized_flag_set_when_surface_differs():
    skills = {s.canonical: s for s in extract_skills("psql database")}
    assert skills["PostgreSQL"].normalized is True
