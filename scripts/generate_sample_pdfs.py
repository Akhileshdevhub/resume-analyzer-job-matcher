"""Generate PDF versions of the synthetic sample resumes.

The sample resumes live as plain text in data/sample_resumes/*.txt (easy to read
and diff). This script renders each into a simple PDF so you have real PDFs to
upload when demoing or screenshotting the app.

Usage (from the repo root):
    python scripts/generate_sample_pdfs.py
"""
from __future__ import annotations

import pathlib

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "sample_resumes"


def text_to_pdf(text: str, out_path: pathlib.Path) -> None:
    c = canvas.Canvas(str(out_path), pagesize=A4)
    width, height = A4
    x, y = 20 * mm, height - 20 * mm
    for raw_line in text.split("\n"):
        line = raw_line.rstrip()
        # Bold-ish look for ALL-CAPS section headings.
        is_heading = line.isupper() and len(line) < 40 and line.strip() != ""
        c.setFont("Helvetica-Bold" if is_heading else "Helvetica", 11 if is_heading else 10)
        c.drawString(x, y, line[:110])
        y -= 6 * mm
        if y < 20 * mm:  # new page
            c.showPage()
            y = height - 20 * mm
    c.save()


def main() -> None:
    for txt in sorted(SRC.glob("*.txt")):
        pdf_path = txt.with_suffix(".pdf")
        text_to_pdf(txt.read_text(), pdf_path)
        print(f"wrote {pdf_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
