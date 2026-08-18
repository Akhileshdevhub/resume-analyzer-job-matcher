"""Tests for text cleaning / normalisation."""
from app.services.text_cleaning import clean_text, normalise_for_matching


def test_clean_collapses_whitespace():
    assert clean_text("a   b\t\tc") == "a b c"


def test_clean_fixes_hyphenation_across_linebreak():
    # "machine-\nlearning" should become "machinelearning" (hyphenated wrap join).
    assert "machinelearning" in clean_text("machine-\nlearning")


def test_clean_normalises_bullets_and_nbsp():
    cleaned = clean_text("• Python developer")
    assert "•" not in cleaned
    assert "Python developer" in cleaned


def test_clean_handles_empty():
    assert clean_text("") == ""


def test_normalise_keeps_special_tokens():
    out = normalise_for_matching("C++, Node.js and C#!")
    assert "c++" in out
    assert "node.js" in out
    assert "c#" in out
