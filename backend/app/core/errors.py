"""Custom application errors.

These give the API a small, meaningful vocabulary of failure types. Each one
carries an HTTP status code and a human-readable message, so the global
exception handler in `main.py` can turn any of them into a clean JSON response
instead of leaking a stack trace to the user.
"""
from __future__ import annotations


class AppError(Exception):
    """Base class for all expected, user-facing errors."""

    status_code: int = 400
    # A short machine-readable code the frontend can branch on if needed.
    code: str = "app_error"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class InvalidFileError(AppError):
    """Uploaded file is the wrong type, empty, or too large."""

    status_code = 422
    code = "invalid_file"


class PDFExtractionError(AppError):
    """The PDF could not be read, or contains no extractable text."""

    status_code = 422
    code = "pdf_extraction_failed"


class EmptyInputError(AppError):
    """Resume text or job description was empty after cleaning."""

    status_code = 422
    code = "empty_input"


class LLMError(AppError):
    """The LLM provider failed. Callers usually catch this and fall back."""

    status_code = 502
    code = "llm_error"
