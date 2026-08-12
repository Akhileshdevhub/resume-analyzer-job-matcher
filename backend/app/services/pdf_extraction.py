"""PDF text extraction.

Turns raw PDF bytes into plain text using `pdfplumber`. We keep this module tiny
and focused: it only extracts text and reports failure clearly. All cleaning and
interpretation happens in later stages.

Why pdfplumber? It reads the PDF text layer directly (no OCR), which is fast and
accurate for the normal case: resumes exported from Word / Google Docs / LaTeX,
which all embed real text. Scanned/photographed resumes have *no* text layer —
we detect that (empty output) and raise a helpful error rather than returning
garbage.
"""
from __future__ import annotations

import io

import pdfplumber

from ..core.errors import PDFExtractionError
from ..core.logging import get_logger

logger = get_logger(__name__)


def extract_text_from_pdf(data: bytes) -> str:
    """Extract concatenated text from all pages of a PDF.

    Args:
        data: raw PDF bytes (already validated by utils.validation).

    Returns:
        The extracted text, pages separated by newlines.

    Raises:
        PDFExtractionError: if the PDF can't be opened or has no text layer.
    """
    pages_text: list[str] = []
    try:
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            for page in pdf.pages:
                # extract_text returns None for pages with no text layer.
                text = page.extract_text() or ""
                pages_text.append(text)
    except PDFExtractionError:
        raise
    except Exception as exc:  # pdfplumber raises a variety of low-level errors
        logger.warning("pdfplumber failed to open the PDF: %s", exc)
        raise PDFExtractionError(
            "We couldn't read this PDF. It may be corrupted or password-protected."
        ) from exc

    full_text = "\n".join(pages_text).strip()

    # A common failure: image-only / scanned PDFs have no extractable text.
    if len(full_text) < 20:
        raise PDFExtractionError(
            "No readable text found in this PDF. If it's a scanned or "
            "image-based resume, please upload a text-based PDF instead."
        )

    logger.info("Extracted %d characters from %d page(s).", len(full_text), len(pages_text))
    return full_text
