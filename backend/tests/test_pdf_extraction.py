"""Tests for PDF extraction and its error handling."""
import pytest

from app.core.errors import InvalidFileError, PDFExtractionError
from app.services.pdf_extraction import extract_text_from_pdf
from app.utils.validation import validate_pdf_upload


def test_extract_text_from_valid_pdf(resume_pdf_bytes):
    text = extract_text_from_pdf(resume_pdf_bytes)
    assert "Python" in text
    assert "Machine Learning" in text


def test_extract_rejects_non_pdf_bytes():
    with pytest.raises(PDFExtractionError):
        extract_text_from_pdf(b"this is definitely not a pdf file, just text")


def test_validation_rejects_wrong_extension(resume_pdf_bytes):
    with pytest.raises(InvalidFileError):
        validate_pdf_upload("resume.docx", "application/pdf", resume_pdf_bytes)


def test_validation_rejects_empty_file():
    with pytest.raises(InvalidFileError):
        validate_pdf_upload("resume.pdf", "application/pdf", b"")


def test_validation_rejects_fake_pdf():
    # Correct extension but not real PDF content (no %PDF signature).
    with pytest.raises(InvalidFileError):
        validate_pdf_upload("resume.pdf", "application/pdf", b"not a real pdf")


def test_validation_accepts_real_pdf(resume_pdf_bytes):
    # Should not raise.
    validate_pdf_upload("resume.pdf", "application/pdf", resume_pdf_bytes)
