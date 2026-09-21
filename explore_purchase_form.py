#!/usr/bin/env python3
"""Crawl PurchaseForm.aspx fields; writes docs/aankoopform-raw.json (gitignored)."""

import json
from pathlib import Path

from playwright.sync_api import sync_playwright

from starterslabo.form_extract import FORM_FIELD_EXTRACT
from starterslabo.purchase import PURCHASE_FORM_URL
from starterslabo.session import load_credentials, login, new_page

OUTPUT = Path(__file__).parent / "docs" / "aankoopform-raw.json"


def main() -> None:
    email, password = load_credentials()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser, page = new_page(p)
        try:
            login(page, email, password)
            page.goto(PURCHASE_FORM_URL, wait_until="networkidle", timeout=60_000)
            page.screenshot(
                path=OUTPUT.parent / "aankoop-form-full.png", full_page=True
            )
            data = page.evaluate(FORM_FIELD_EXTRACT)
            OUTPUT.write_text(
                json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            print(f"Wrote {OUTPUT} ({len(data['fields'])} fields)")
        finally:
            browser.close()


if __name__ == "__main__":
    main()
