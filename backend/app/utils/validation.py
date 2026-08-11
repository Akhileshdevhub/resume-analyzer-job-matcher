"""Upload validation helpers.

Security-relevant: we never trust an uploaded file. Before touching the bytes we
check the declared type, the extension, and the size. We also sniff the PDF
magic number (`%PDF`) so a file merely *named* `.pdf` can't slip through.
"""
from __future__ import annotations

from ..core.config import get_settings
from ..core.errors import InvalidFileError

PDF_MAGIC = b"%PDF"
ALLOWED_CONTENT_TYPES = {"application/pdf", "application/x-pdf"}


def validate_pdf_upload(filename: str, content_type: str | None, data: bytes) -> None:
    """Raise InvalidFileError if the upload is not an acceptable PDF.

    Checks, in order: non-empty, extension, declared content type, size limit,
    and the real PDF magic number. Raising early means the parsing code below
    only ever sees plausible PDFs.
    """
    settings = get_settings()

    if not data:
        raise InvalidFileError("The uploaded file is empty.")

    if not filename.lower().endswith(".pdf"):
        raise InvalidFileError("Only PDF resumes are supported (expected a .pdf file).")

    # content_type can be spoofed, so it's a soft check; the magic number below
    # is the real gate.
    if content_type and content_type.lower() not in ALLOWED_CONTENT_TYPES:
        raise InvalidFileError(
            f"Unexpected file type '{content_type}'. Please upload a PDF."
        )

    if len(data) > settings.max_upload_bytes:
        raise InvalidFileError(
            f"File is too large ({len(data) / 1_048_576:.1f} MB). "
            f"Maximum is {settings.max_upload_mb} MB."
        )

    if not data.startswith(PDF_MAGIC):
        raise InvalidFileError(
            "This file does not look like a valid PDF (missing PDF signature)."
        )
