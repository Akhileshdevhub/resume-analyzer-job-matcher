"""Text cleaning / normalisation.

Raw PDF text is messy: inconsistent whitespace, words split across line breaks
with hyphens, bullet glyphs, and non-breaking spaces. Every later stage (section
detection, skill matching, embeddings) works better on clean, consistent input,
so we normalise once here, up front.

The functions are deliberately simple and side-effect free, which makes them
trivial to unit test.
"""
from __future__ import annotations

import re

# Characters PDFs love to sprinkle in: bullets, non-breaking spaces, zero-width.
_BULLETS = "•·▪◦‣∙"
_ZERO_WIDTH = "​‌‍﻿"


def _fix_hyphenation(text: str) -> str:
    """Join words split across a line break by a hyphen: "machine-\nlearning".

    We only join when a lowercase letter precedes the hyphen and a letter
    follows the newline, to avoid mangling real hyphenated tokens.
    """
    return re.sub(r"([a-z])-\n([a-zA-Z])", r"\1\2", text)


def clean_text(text: str) -> str:
    """Return a normalised version of `text`.

    Steps: unify newlines, join hyphenated line breaks, drop zero-width chars,
    convert bullets and non-breaking spaces to plain spaces, collapse runs of
    spaces, and trim trailing whitespace on each line.
    """
    if not text:
        return ""

    # Normalise newlines.
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    text = _fix_hyphenation(text)

    # Strip zero-width characters entirely.
    for ch in _ZERO_WIDTH:
        text = text.replace(ch, "")

    # Bullets and non-breaking spaces become ordinary spaces.
    for ch in _BULLETS:
        text = text.replace(ch, " ")
    text = text.replace(" ", " ")

    # Collapse horizontal whitespace (spaces/tabs) but keep newlines.
    text = re.sub(r"[ \t]+", " ", text)
    # Trim spaces at the ends of each line.
    text = "\n".join(line.strip() for line in text.split("\n"))
    # Collapse 3+ blank lines into a single blank line.
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def normalise_for_matching(text: str) -> str:
    """Lowercased, punctuation-light form used for keyword/skill matching.

    Kept separate from `clean_text` because embeddings and display want the
    nicely-cased version, while dictionary matching wants an aggressive
    lowercase form.
    """
    text = text.lower()
    # Replace anything that isn't a letter, digit, +, # or . with a space.
    # (Keeps tokens like "c++", "c#", "node.js" intact.)
    text = re.sub(r"[^a-z0-9+#.\-/ ]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()
