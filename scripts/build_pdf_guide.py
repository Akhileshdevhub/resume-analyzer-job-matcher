"""Build the polished 'Technical & Interview Guide' PDF from the markdown docs.

Pipeline: markdown -> HTML (python-markdown) -> styled HTML -> PDF (wkhtmltopdf).
Run from the repo root:  python scripts/build_pdf_guide.py
"""
from __future__ import annotations

import pathlib
import subprocess

import markdown

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUT_HTML = DOCS / "_guide_build.html"
OUT_PDF = DOCS / "AI-Resume-Analyzer-Technical-and-Interview-Guide.pdf"

# Order of the combined document.
SECTIONS = [
    ("INTERVIEW_GUIDE.md", None),
    ("ARCHITECTURE.md", "Appendix A — System Architecture"),
    ("SCORING.md", "Appendix B — Scoring Methodology"),
    ("CONCEPTS.md", "Appendix C — Concepts & Design Decisions"),
]

CSS = """
@page { margin: 20mm 16mm; }
* { box-sizing: border-box; }
body {
  font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
  font-size: 10.5pt; line-height: 1.5; color: #1e293b; max-width: 100%;
}
h1 { font-size: 20pt; color: #0f172a; border-bottom: 3px solid #4f46e5;
     padding-bottom: 6px; margin-top: 0; page-break-before: always; }
h1:first-of-type { page-break-before: avoid; }
h2 { font-size: 14pt; color: #3730a3; margin-top: 22px; border-bottom: 1px solid #e2e8f0; padding-bottom: 3px; }
h3 { font-size: 12pt; color: #0f172a; margin-top: 16px; }
h4 { font-size: 10.5pt; color: #475569; margin-top: 12px; }
p, li { color: #1e293b; }
a { color: #4f46e5; text-decoration: none; }
code { font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', monospace;
       font-size: 9pt; background: #f1f5f9; padding: 1px 4px; border-radius: 3px; color: #0f172a; }
pre { background: #0f172a; color: #e2e8f0; padding: 12px; border-radius: 6px;
      overflow-x: auto; font-size: 8.5pt; line-height: 1.4; page-break-inside: avoid; }
pre code { background: none; color: inherit; padding: 0; font-size: 8.5pt; }
table { border-collapse: collapse; width: 100%; margin: 10px 0; font-size: 9.5pt; page-break-inside: avoid; }
th, td { border: 1px solid #cbd5e1; padding: 6px 8px; text-align: left; vertical-align: top; }
th { background: #eef2ff; color: #3730a3; }
blockquote { border-left: 4px solid #4f46e5; margin: 10px 0; padding: 6px 14px;
             background: #f8fafc; color: #334155; }
hr { border: none; border-top: 1px solid #e2e8f0; margin: 18px 0; }
strong { color: #0f172a; }
"""

TITLE_HTML = """
<div style="page-break-after: always; text-align:center; padding-top: 60mm;">
  <div style="font-size: 30pt; font-weight: 800; color:#0f172a; line-height:1.2;">
    AI Resume Analyzer<br/>&amp; Job Matcher
  </div>
  <div style="font-size: 15pt; color:#4f46e5; margin-top: 14px; font-weight:600;">
    Technical &amp; Interview Guide
  </div>
  <div style="font-size: 11pt; color:#475569; margin-top: 28px; max-width: 130mm; margin-left:auto; margin-right:auto;">
    An explainable resume-to-job matching system built with FastAPI, React,
    and scikit-learn. This guide covers the architecture, the ML/NLP pipeline,
    the scoring methodology, a full code walkthrough, and a complete interview
    question bank.
  </div>
  <div style="font-size: 10pt; color:#94a3b8; margin-top: 40px;">
    Portfolio project by Ayush
  </div>
</div>
"""


def md_to_html(text: str) -> str:
    return markdown.markdown(
        text, extensions=["tables", "fenced_code", "toc", "sane_lists"]
    )


def main() -> None:
    parts = [TITLE_HTML]
    for filename, heading in SECTIONS:
        raw = (DOCS / filename).read_text()
        if heading:
            raw = f"# {heading}\n\n" + raw
        parts.append(md_to_html(raw))

    html = (
        "<!doctype html><html><head><meta charset='utf-8'>"
        f"<style>{CSS}</style></head><body>" + "\n".join(parts) + "</body></html>"
    )
    OUT_HTML.write_text(html)

    subprocess.run(
        [
            "wkhtmltopdf",
            "--enable-local-file-access",
            "--margin-top", "18mm",
            "--margin-bottom", "16mm",
            "--quiet",
            str(OUT_HTML),
            str(OUT_PDF),
        ],
        check=True,
    )
    print("wrote", OUT_PDF.relative_to(ROOT))


if __name__ == "__main__":
    main()
