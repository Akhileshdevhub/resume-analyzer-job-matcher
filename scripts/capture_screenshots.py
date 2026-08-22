"""Capture real screenshots of the running app for the README.

Assumes the backend is on :8000 and the built frontend is served on :5173.
Run from the repo root after both are up:
    python scripts/capture_screenshots.py
"""
from __future__ import annotations

import pathlib

from playwright.sync_api import sync_playwright

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets" / "screenshots"
OUT.mkdir(parents=True, exist_ok=True)
URL = "http://localhost:5173/"


def shot(page, name):
    page.screenshot(path=str(OUT / name))
    print("saved", name)


def element_shot(page, selector, name):
    el = page.query_selector(selector)
    if el:
        el.screenshot(path=str(OUT / name))
        print("saved", name)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 900}, device_scale_factor=2)

        page.goto(URL, wait_until="networkidle")
        page.wait_for_timeout(500)
        shot(page, "01-landing.png")

        # Fill in a sample and analyse.
        page.get_by_role("button", name="Load a sample").click()
        page.wait_for_timeout(400)
        shot(page, "02-form-filled.png")

        page.get_by_role("button", name="Analyze match").click()
        page.wait_for_selector("text=Why this score", timeout=15000)
        page.wait_for_timeout(1200)  # let the gauge/bars animate

        shot(page, "03-dashboard-top.png")
        page.screenshot(path=str(OUT / "04-dashboard-full.png"), full_page=True)

        # Scroll to sections and crop cards.
        element_shot(page, "div.card:has-text('Why this score')", "05-score-breakdown.png")
        element_shot(page, "div.card:has-text('Skills')", "06-skills.png")
        element_shot(page, "div.card:has-text('Recommendations')", "07-recommendations.png")
        element_shot(page, "div.card:has-text('Interview preparation')", "08-interview.png")

        browser.close()


if __name__ == "__main__":
    main()
